"""Upsert de producto compartido entre los workers de refresco de cada
cadena — MercadonaProduct y DiaProduct tienen la misma forma (external_id,
name, top_category, category, unit, price, image_url), así que no hace
falta duplicar esta lógica por cadena."""

from typing import Protocol

from sqlalchemy.orm import Session

from app.models import Product, utcnow


class CatalogItem(Protocol):
    external_id: str
    name: str
    top_category: str
    category: str
    unit: str | None
    price: float
    image_url: str | None


def upsert_product(db: Session, chain: str, item: CatalogItem) -> Product:
    product = (
        db.query(Product)
        .filter(Product.chain == chain, Product.external_id == item.external_id)
        .first()
    )
    if product is None:
        product = Product(
            chain=chain,
            external_id=item.external_id,
            name=item.name,
            top_category=item.top_category,
            category=item.category,
            unit=item.unit,
            image_url=item.image_url,
        )
        db.add(product)
        db.flush()
    else:
        product.name = item.name
        product.top_category = item.top_category
        product.category = item.category
        product.unit = item.unit
        product.image_url = item.image_url
    product.current_price = item.price
    product.current_price_captured_at = utcnow()
    return product
