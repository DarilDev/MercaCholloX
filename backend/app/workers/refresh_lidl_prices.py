"""Actualiza la caché local con precios reales de Lidl España (Open Prices).

Uso: python -m app.workers.refresh_lidl_prices

A diferencia de Mercadona/Dia/HiperDino/Aldi, esto no es ni un catálogo ni un
folleto — son precios sueltos enviados por la comunidad a Open Prices (ver
services/lidl_client.py). Cobertura deliberadamente modesta, documentada así.
"""

from app.db import SessionLocal
from app.models import Price
from app.services import lidl_client
from app.workers.common import upsert_product


def refresh() -> int:
    db = SessionLocal()
    count = 0
    try:
        products = lidl_client.fetch_lidl_products()
        for item in products:
            product = upsert_product(db, "lidl", item)
            db.add(Price(product_id=product.id, store_id=None, price=item.price))
            count += 1
        db.commit()
    finally:
        db.close()
    return count


if __name__ == "__main__":
    total = refresh()
    print(f"Total productos actualizados: {total}")
