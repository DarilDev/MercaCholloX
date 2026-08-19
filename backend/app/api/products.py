from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Price, Product
from app.schemas import CategoryOut, ProductOut

router = APIRouter(tags=["products"])


def _latest_price_query(db: Session):
    latest_price_ids = (
        db.query(Price.product_id, func.max(Price.id).label("latest_id"))
        .group_by(Price.product_id)
        .subquery()
    )
    return (
        db.query(Product, Price.price)
        .join(latest_price_ids, Product.id == latest_price_ids.c.product_id)
        .join(Price, Price.id == latest_price_ids.c.latest_id)
    )


def _to_product_out(product: Product, price: float) -> ProductOut:
    return ProductOut(
        id=product.id,
        chain=product.chain,
        external_id=product.external_id,
        name=product.name,
        top_category=product.top_category,
        category=product.category,
        unit=product.unit,
        image_url=product.image_url,
        price=price,
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
    query = _latest_price_query(db)
    if top_category:
        query = query.filter(Product.top_category == top_category)
    if category:
        query = query.filter(Product.category == category)
    rows = query.order_by(Product.name).limit(200).all()
    return [_to_product_out(product, price) for product, price in rows]


@router.get("/products/search", response_model=list[ProductOut])
def search_products(q: str = Query(min_length=2), db: Session = Depends(get_db)):
    """Busca por substring en la caché local (la API de Mercadona no ofrece
    búsqueda libre, solo navegación por categorías — ver docs/ARCHITECTURE.md)."""
    rows = (
        _latest_price_query(db)
        .filter(Product.name.ilike(f"%{q}%"))
        .order_by(Product.name)
        .limit(50)
        .all()
    )
    return [_to_product_out(product, price) for product, price in rows]
