"""Actualiza la caché local con precios reales de Aldi (products + prices).

Uso: python -m app.workers.refresh_aldi_prices

A diferencia de Mercadona/Dia/HiperDino, Aldi no tiene catálogo navegable ni
buscable — solo el folleto de ofertas de la semana en curso (ver
services/aldi_client.py). Una sola petición trae todo lo disponible, no hace
falta iterar términos. Pensado para correr aislado del backend (GitHub
Actions), nunca dentro del proceso de la API.
"""

from app.db import SessionLocal
from app.models import Price
from app.services import aldi_client
from app.workers.common import upsert_product


def refresh() -> int:
    db = SessionLocal()
    count = 0
    try:
        products = aldi_client.fetch_offers()
        for item in products:
            product = upsert_product(db, "aldi", item)
            db.add(Price(product_id=product.id, store_id=None, price=item.price))
            count += 1
        db.commit()
    finally:
        db.close()
    return count


if __name__ == "__main__":
    total = refresh()
    print(f"Total productos actualizados: {total}")
