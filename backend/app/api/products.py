from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Product
from app.schemas import CategoryOut, PriceHistoryOut, PricePointOut, ProductOut
from app.services import price_history
from app.services.shopping_list import known_chains
from app.services.text_matching import significant_words

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


def _best_match(db: Session, name: str) -> Product | None:
    """Empareja un nombre externo (ej. de OpenFoodFacts) contra la caché
    local. Antes anclaba solo en la primera palabra del nombre — con
    productos de cadenas que no tenemos integradas (ej. Lidl) eso enganchaba
    cualquier producto de otra cadena que compartiera esa única palabra (ej.
    "leche" pillaba una leche de Mercadona sin relación real, confundiendo al
    usuario con un precio que no es el del producto escaneado). Ahora exige
    TODAS las palabras significativas del nombre (como el matching de
    favoritos en shopping_list.py) y al menos 2, para no anclar en una sola
    palabra genérica — devolver None es preferible a adivinar mal."""
    words = significant_words(name)
    if len(words) < 2:
        return None
    query = db.query(Product).filter(Product.current_price.isnot(None))
    for word in words:
        query = query.filter(Product.name.ilike(f"%{word}%"))
    candidates = query.limit(200).all()
    if not candidates:
        return None
    candidates.sort(key=lambda p: len(p.name.lower().split()))
    return candidates[0]


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


@router.get("/products/{product_id}/price_history", response_model=PriceHistoryOut)
def product_price_history(product_id: int, db: Session = Depends(get_db)):
    """Historial completo de precios de un producto (tabla `prices`,
    append-only desde el principio) + una etiqueta que distingue una
    bajada real de "el mismo precio de siempre" — inspirado en cómo la
    comunidad de Chollometro compara contra el histórico a mano."""
    history = price_history.get_history(db, product_id)
    return PriceHistoryOut(
        points=[
            PricePointOut(price=p.price, captured_at=p.captured_at.isoformat())
            for p in history
        ],
        discount_label=price_history.discount_label(history),
    )


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
