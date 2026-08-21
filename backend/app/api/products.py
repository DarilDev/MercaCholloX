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
def list_categories(chain: str, db: Session = Depends(get_db)):
    """Pasillos de una cadena, con su propia taxonomía real (top_category) —
    navegación cadena primero, elegida por Daril en vez del pasillo unificado
    entre cadenas (ver docs/DECISIONS.md). `canonical_category`/
    `category_mapping.py` se dejan sin usar por si se recupera esta vista más
    adelante, no se borran."""

    rows = (
        db.query(Product.top_category, func.count(Product.id))
        .filter(
            Product.chain == chain,
            Product.top_category.isnot(None),
            Product.current_price.isnot(None),
        )
        .group_by(Product.top_category)
        .all()
    )
    return [
        CategoryOut(name=name, count=count) for name, count in sorted(rows, key=lambda r: r[0])
    ]


@router.get("/products", response_model=list[ProductOut])
def list_products(chain: str, category: str, db: Session = Depends(get_db)):
    """Productos de un pasillo de una cadena concreta."""
    products = (
        db.query(Product)
        .filter(
            Product.chain == chain,
            Product.top_category == category,
            Product.current_price.isnot(None),
        )
        .order_by(Product.name)
        .limit(300)
        .all()
    )
    return [_to_product_out(p) for p in products]


@router.get("/products/search", response_model=list[ProductOut])
def search_products(q: str = Query(min_length=2), db: Session = Depends(get_db)):
    """Busca por substring en la caché local, entre todas las cadenas — a
    diferencia de la navegación por pasillos, aquí sí tiene sentido comparar
    a simple vista qué hay en cada una (la ficha ya indica la cadena).

    Ordenado por relevancia (menos palabras de más en el nombre, mismo
    criterio ya usado en el matching de favoritos de shopping_list.py) en
    vez de alfabético — alfabético enterraba los productos reales bajo
    coincidencias parciales (ej. "aceite" solo enseñaba cosméticos tipo
    "Aceite bruma protectora Sunnique" antes que aceite de oliva de verdad,
    porque "bruma" va antes que "de" alfabéticamente)."""
    products = (
        db.query(Product)
        .filter(Product.current_price.isnot(None), Product.name.ilike(f"%{q}%"))
        .limit(500)
        .all()
    )
    products.sort(key=lambda p: len(p.name.split()))
    return [_to_product_out(p) for p in products[:50]]
