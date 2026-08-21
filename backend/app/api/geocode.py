from fastapi import APIRouter, Query

from app.schemas import GeocodeResultOut
from app.services import geocoding_client

router = APIRouter(tags=["geocode"])


@router.get("/geocode", response_model=list[GeocodeResultOut])
def geocode(q: str = Query(min_length=3)):
    """Busca direcciones reales por texto (Photon, con Nominatim de respaldo)
    — para fijar casa/trabajo escribiendo, sin depender del GPS."""
    try:
        results = geocoding_client.search(q)
    except geocoding_client.GeocodingClientError:
        return []
    return [
        GeocodeResultOut(label=r.label, lat=r.lat, lon=r.lon) for r in results
    ]
