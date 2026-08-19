from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Product
from app.schemas import CategoryOut, ProductOut

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


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Pasillos del supermercado (categorías top-level) con sus subcategorías,
    para navegar como en una tienda real en vez de buscar por texto libre."""

    rows = (
        db.query(Product.top_category, Product.category)
        .filter(Product.top_category.isnot(None))
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
    top_category: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Productos de un pasillo/subcategoría — navegación tipo supermercado."""
    query = db.query(Product).filter(Product.current_price.isnot(None))
    if top_category:
        query = query.filter(Product.top_category == top_category)
    if category:
        query = query.filter(Product.category == category)
    products = query.order_by(Product.name).limit(200).all()
    return [_to_product_out(p) for p in products]


@router.get("/products/search", response_model=list[ProductOut])
def search_products(q: str = Query(min_length=2), db: Session = Depends(get_db)):
    """Busca por substring en la caché local (la API de Mercadona no ofrece
    búsqueda libre, solo navegación por categorías — ver docs/ARCHITECTURE.md)."""
    products = (
        db.query(Product)
        .filter(Product.current_price.isnot(None), Product.name.ilike(f"%{q}%"))
        .order_by(Product.name)
        .limit(50)
        .all()
    )
    return [_to_product_out(p) for p in products]
