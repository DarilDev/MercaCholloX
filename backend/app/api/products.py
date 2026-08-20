from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
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
    """Cadenas con datos cacheados."""
    return known_chains(db)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Pasillos comunes a todas las cadenas (ver services/category_mapping.py)
    — navegar por pasillo enseña productos de todas las cadenas juntos, para
    comparar de un vistazo en vez de tener que elegir cadena primero."""

    rows = (
        db.query(Product.canonical_category, Product.chain, func.count(Product.id))
        .filter(Product.canonical_category.isnot(None), Product.current_price.isnot(None))
        .group_by(Product.canonical_category, Product.chain)
        .all()
    )

    by_category: dict[str, dict[str, int]] = {}
    for canonical, chain, count in rows:
        by_category.setdefault(canonical, {})[chain] = count

    return [
        CategoryOut(name=name, chains=chains) for name, chains in sorted(by_category.items())
    ]


@router.get("/products", response_model=list[ProductOut])
def list_products(category: str, db: Session = Depends(get_db)):
    """Productos de un pasillo común, de todas las cadenas juntos — ordenados
    por nombre para que productos parecidos de cadenas distintas caigan cerca
    y se puedan comparar a simple vista."""
    products = (
        db.query(Product)
        .filter(Product.canonical_category == category, Product.current_price.isnot(None))
        .order_by(Product.name)
        .limit(300)
        .all()
    )
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
