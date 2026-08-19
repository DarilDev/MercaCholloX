"""Recorre el catálogo de Mercadona y actualiza la caché local (products + prices).

Uso: python -m app.workers.refresh_prices [--wh mad1] [--limit N]

`--limit` restringe a las primeras N categorías hoja — útil para probar rápido
sin recorrer las ~100+ categorías completas.
"""

import argparse
import random
import time

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Price, Product, utcnow
from app.services import mercadona_client as mc


def upsert_product(db: Session, item: mc.MercadonaProduct) -> Product:
    product = (
        db.query(Product)
        .filter(Product.chain == "mercadona", Product.external_id == item.external_id)
        .first()
    )
    if product is None:
        product = Product(
            chain="mercadona",
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


def refresh(wh: str | None = None, limit: int | None = None) -> int:
    db = SessionLocal()
    count = 0
    try:
        leaves = mc.fetch_leaf_category_ids(wh)
        if limit:
            leaves = leaves[:limit]

        for category_id, category_name, top_category_name in leaves:
            try:
                products = mc.fetch_category_products(category_id, top_category_name, wh)
            except mc.MercadonaBlockedError:
                # Nos han limitado/bloqueado: seguir insistiendo es lo peor que se
                # puede hacer (ver docstring del cliente) — parar el run entero.
                print(f"  !! BLOQUEADO por Mercadona en categoría {category_id} — abortando el refresco.", flush=True)
                raise
            except Exception as exc:  # fallo puntual de una categoría, no de toda la fuente
                print(f"  ! error en categoría {category_id} ({category_name}): {exc}", flush=True)
                continue

            for item in products:
                product = upsert_product(db, item)
                db.add(Price(product_id=product.id, store_id=None, price=item.price))
                count += 1

            db.commit()
            print(f"  {category_name}: {len(products)} productos", flush=True)
            time.sleep(0.2 + random.uniform(0, 0.3))  # ritmo con jitter, no perfectamente regular
    finally:
        db.close()
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wh", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    total = refresh(wh=args.wh, limit=args.limit)
    print(f"Total productos actualizados: {total}")
