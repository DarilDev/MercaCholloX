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

# Caja grosera antes del haversine exacto (mismo criterio que worth_it.py /
# fuel lookup) — evita traer toda la tabla stores en cada petición.
_CACHE_BOX_DEG = 0.15  # ~16km


def _cached_nearby(db: Session, lat: float, lon: float, radius_km: float) -> list[Store]:
    """Si ya hay tiendas cacheadas cerca (de una visita anterior a esta zona,
    o de una llamada de worth_it.py), se sirven directas — sin esto, cada
    vez que se abre Ubicación toca esperar a Overpass en vivo (varios
    segundos, a veces bastantes más si el primer mirror está caído), aunque
    la zona ya se hubiera consultado antes y las tiendas físicas no se muevan
    de un día para otro. Simplificación aceptada: si esta zona se cacheó
    antes con un radio menor al pedido ahora, el resultado puede quedarse
    corto — no ocurre hoy porque la app siempre pide el mismo radio."""
    candidates = (
        db.query(Store)
        .filter(Store.lat.isnot(None), Store.lon.isnot(None))
        .filter(Store.lat.between(lat - _CACHE_BOX_DEG, lat + _CACHE_BOX_DEG))
        .filter(Store.lon.between(lon - _CACHE_BOX_DEG, lon + _CACHE_BOX_DEG))
        .all()
    )
    return [s for s in candidates if haversine_km(lat, lon, s.lat, s.lon) <= radius_km]


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
    stores = _cached_nearby(db, lat, lon, radius_km)

    if not stores:
        try:
            nearby = overpass_client.fetch_nearby_supermarkets(lat, lon, radius_m=int(radius_km * 1000))
        except overpass_client.OverpassClientError:
            return []
        _upsert_stores(db, nearby)
        stores = _cached_nearby(db, lat, lon, radius_km)

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
        for store in stores
    ]
    out.sort(key=lambda s: s.distance_km)
    return out
