"""Refresca la caché de precios de combustible (MITECO) — ver
app/services/miteco_client.py. Se recomienda diario: las gasolineras están
obligadas por ley a reportar cambios en 24h, no hace falta más frecuencia.

~11.000 estaciones en una sola pasada — a diferencia de Mercadona/Dia (que
llegan en lotes pequeños por categoría/término de búsqueda), aquí sí hace
falta upsert por lotes en vez de fila a fila: contra una base de datos en
red (Neon), un SELECT+INSERT/UPDATE por fila tarda minutos y en la práctica
no termina en un tiempo razonable.

Uso: python -m app.workers.refresh_fuel_prices
"""

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.db import SessionLocal, engine
from app.models import FuelStation, utcnow
from app.services import miteco_client as mc

_BATCH_SIZE = 500


def _upsert_batch(db, rows: list[dict]) -> None:
    insert_fn = sqlite_insert if engine.dialect.name == "sqlite" else pg_insert
    stmt = insert_fn(FuelStation).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["external_id"],
        set_={
            "name": stmt.excluded.name,
            "lat": stmt.excluded.lat,
            "lon": stmt.excluded.lon,
            "gasoleo_a": stmt.excluded.gasoleo_a,
            "gasolina_95_e5": stmt.excluded.gasolina_95_e5,
            "updated_at": stmt.excluded.updated_at,
        },
    )
    db.execute(stmt)


def refresh() -> int:
    db = SessionLocal()
    count = 0
    try:
        stations = mc.fetch_all_stations()
        now = utcnow()
        for i in range(0, len(stations), _BATCH_SIZE):
            batch = stations[i : i + _BATCH_SIZE]
            rows = [
                {
                    "external_id": s.external_id,
                    "name": s.name,
                    "lat": s.lat,
                    "lon": s.lon,
                    "gasoleo_a": s.gasoleo_a,
                    "gasolina_95_e5": s.gasolina_95_e5,
                    "updated_at": now,
                }
                for s in batch
            ]
            _upsert_batch(db, rows)
            db.commit()
            count += len(rows)
    finally:
        db.close()
    return count


if __name__ == "__main__":
    total = refresh()
    print(f"Total gasolineras actualizadas: {total}")
