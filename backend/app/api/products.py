from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Product
from app.schemas import CategoryOut, ProductOut
from app.services.shopping_list import known_chains

router = APIRouter(tags=["products"])


def _to_product_out(product: Product) -> ProductOut:
    return ProductOut(
        id=product.id,
        chain=product.chain,
        external_id=product.external_id,
        name=product.name,
        top_category=product.top_category,
        category=product.category,
        unit=product.unit,
        image_url=product.image_url,
        price=product.current_price,
    )


@router.get("/chains", response_model=list[str])
def list_chains(db: Session = Depends(get_db)):
    """Cadenas con datos cacheados — cada una tiene su propia taxonomía de
    pasillos/categorías, no tiene sentido mezclarlas al navegar."""
    return known_chains(db)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(chain: str, db: Session = Depends(get_db)):
    """Pasillos de una cadena (categorías top-level) con sus subcategorías,
    para navegar como en una tienda real en vez de buscar por texto libre.
    Cada cadena tiene su propia taxonomía — mezclarlas no tendría sentido."""

    rows = (
        db.query(Product.top_category, Product.category)
        .filter(Product.chain == chain, Product.top_category.isnot(None))
        .distinct()
        .all()
    )

    by_top: dict[str, set[str]] = {}
    for top, sub in rows:
        by_top.setdefault(top, set()).add(sub)

    return [
        CategoryOut(name=top, subcategories=sorted(subs))
        for top, subs in sorted(by_top.items())
    ]


@router.get("/products", response_model=list[ProductOut])
def list_products(
    chain: str,
    top_category: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Productos de un pasillo/subcategoría de una cadena — navegación tipo supermercado."""
    query = db.query(Product).filter(Product.chain == chain, Product.current_price.isnot(None))
    if top_category:
        query = query.filter(Product.top_category == top_category)
    if category:
        query = query.filter(Product.category == category)
    products = query.order_by(Product.name).limit(200).all()
    return [_to_product_out(p) for p in products]


@router.get("/products/search", response_model=list[ProductOut])
def search_products(q: str = Query(min_length=2), db: Session = Depends(get_db)):
    """Busca por substring en la caché local, entre todas las cadenas — a
    diferencia de la navegación por pasillos, aquí sí tiene sentido comparar
    a simple vista qué hay en cada una (la ficha ya indica la cadena)."""
    products = (
        db.query(Product)
        .filter(Product.current_price.isnot(None), Product.name.ilike(f"%{q}%"))
        .order_by(Product.name)
        .limit(50)
        .all()
    )
    return [_to_product_out(p) for p in products]
