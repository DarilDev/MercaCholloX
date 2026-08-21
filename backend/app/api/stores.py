from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Store
from app.schemas import StoreOut
from app.services import overpass_client
from app.services.chain_aliases import normalize_chain_name
from app.services.geo import haversine_km

router = APIRouter(prefix="/stores", tags=["stores"])


def _upsert_store(db: Session, item: overpass_client.NearbyStore) -> Store:
    raw_chain = (item.brand or item.name).strip().lower()
    # Normalizado a la cadena canónica cuando la reconocemos (mercadona/dia)
    # — así worth_it.py puede reutilizar esta caché sin volver a llamar a
    # Overpass. Las cadenas que no trackeamos todavía (Carrefour, HiperDino...)
    # se guardan con su nombre real tal cual, para seguir mostrándolas en
    # "súper cercanos" aunque no tengamos precios suyos.
    chain = normalize_chain_name(raw_chain) or raw_chain
    store = (
        db.query(Store)
        .filter(Store.chain == chain, Store.external_id == item.external_id)
        .first()
    )
    if store is None:
        store = Store(chain=chain, external_id=item.external_id, name=item.name)
        db.add(store)
    store.lat = item.lat
    store.lon = item.lon
    return store


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

    stores = [_upsert_store(db, item) for item in nearby]
    db.commit()

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
