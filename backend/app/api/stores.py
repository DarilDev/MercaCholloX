from fastapi import APIRouter, Depends, Query
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.models import Store
from app.schemas import StoreOut
from app.services import overpass_client
from app.services.chain_aliases import normalize_chain_name
from app.services.geo import haversine_km

router = APIRouter(prefix="/stores", tags=["stores"])


def _upsert_stores(db: Session, nearby: list[overpass_client.NearbyStore]) -> None:
    """Upsert por lotes, no fila a fila — con ~450 tiendas en una zona densa
    (ej. Madrid), un SELECT+INSERT/UPDATE por fila contra Neon tarda minutos
    y en la práctica no termina en un tiempo razonable (mismo problema ya
    resuelto para gasolineras en workers/refresh_fuel_prices.py; aquí pasaba
    inadvertido porque nadie había medido cuánto tardaba /stores/nearby de
    verdad hasta que se investigó por qué fallaba desde Render)."""
    if not nearby:
        return
    rows = []
    for item in nearby:
        raw_chain = (item.brand or item.name).strip().lower()
        # Normalizado a la cadena canónica cuando la reconocemos (mercadona/
        # dia) — así worth_it.py puede reutilizar esta caché sin volver a
        # llamar a Overpass. Las cadenas que no trackeamos todavía
        # (Carrefour, HiperDino...) se guardan con su nombre real tal cual.
        chain = normalize_chain_name(raw_chain) or raw_chain
        rows.append(
            {
                "chain": chain,
                "external_id": item.external_id,
                "name": item.name,
                "lat": item.lat,
                "lon": item.lon,
            }
        )
    insert_fn = sqlite_insert if engine.dialect.name == "sqlite" else pg_insert
    stmt = insert_fn(Store).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["chain", "external_id"],
        set_={"name": stmt.excluded.name, "lat": stmt.excluded.lat, "lon": stmt.excluded.lon},
    )
    db.execute(stmt)
    db.commit()


@router.get("/nearby", response_model=list[StoreOut])
def nearby_stores(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(3.0, gt=0, le=10),
    db: Session = Depends(get_db),
):
    """Supermercados físicos reales cerca de una coordenada (OpenStreetMap
    Overpass). Distancia en línea recta — para tiempo/distancia de
    conducción real de un candidato concreto, ver /stores/{id}/route
    (Fase 5, motor de scoring)."""
    try:
        nearby = overpass_client.fetch_nearby_supermarkets(lat, lon, radius_m=int(radius_km * 1000))
    except overpass_client.OverpassClientError:
        return []

    _upsert_stores(db, nearby)

    external_ids = [item.external_id for item in nearby]
    cached = {
        store.external_id: store
        for store in db.query(Store).filter(Store.external_id.in_(external_ids)).all()
    }

    out = [
        StoreOut(
            id=store.id,
            chain=store.chain,
            name=store.name,
            address=store.address,
            lat=store.lat,
            lon=store.lon,
            distance_km=haversine_km(lat, lon, store.lat, store.lon),
        )
        for store in cached.values()
    ]
    out.sort(key=lambda s: s.distance_km)
    return out
