"""Actualiza la caché local con precios reales de HiperDino (products + prices).

Uso: python -m app.workers.refresh_hiperdino_prices [--limit N]

Igual que Dia, se recorre buscando una lista de términos habituales (ver
services/hiperdino_client.SEARCH_TERMS) — no se encontró un árbol de
categorías navegable vía GraphQL. Pensado para correr aislado del backend
(GitHub Actions), nunca dentro del proceso de la API.
"""

import argparse
import random
import time

from app.db import SessionLocal
from app.models import Price
from app.services import hiperdino_client
from app.workers.common import upsert_product


def refresh(limit: int | None = None) -> int:
    db = SessionLocal()
    count = 0
    try:
        terms = hiperdino_client.SEARCH_TERMS
        if limit:
            terms = terms[:limit]

        for term in terms:
            try:
                products = hiperdino_client.search_products(term)
            except hiperdino_client.HiperdinoBlockedError:
                print(f"  !! BLOQUEADO por HiperDino buscando '{term}' — abortando el refresco.", flush=True)
                raise
            except Exception as exc:  # fallo puntual de un término, no de toda la fuente
                print(f"  ! error buscando '{term}': {exc}", flush=True)
                continue

            for item in products:
                product = upsert_product(db, "hiperdino", item)
                db.add(Price(product_id=product.id, store_id=None, price=item.price))
                count += 1

            db.commit()
            print(f"  {term}: {len(products)} productos", flush=True)
            time.sleep(0.3 + random.uniform(0, 0.4))
    finally:
        db.close()
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    total = refresh(limit=args.limit)
    print(f"Total productos actualizados: {total}")
