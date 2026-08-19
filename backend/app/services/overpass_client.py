"""Cliente para la API pública de Overpass (OpenStreetMap) — localiza
supermercados físicos reales cerca de una coordenada. Gratis, sin key.

Verificado a mano contra la API real: POST a /api/interpreter con una query
Overpass QL, devuelve nodos `shop=supermarket` con `name`/`brand` cuando OSM
los tiene mapeados (no todos los tienen).

El servidor público de Overpass responde de forma inconsistente bajo
peticiones repetidas seguidas (406 unas veces, 504 otras, verificado a
mano) — probablemente por ser un servicio demo/comunitario con carga
variable, no un fallo del cliente. Se reintenta con backoff en vez de
tratarlo como un error definitivo a la primera.
"""

import random
import time
from dataclasses import dataclass

import httpx

from app.config import settings

_MAX_RETRIES = 3
_BASE_DELAY_S = 1.5


class OverpassClientError(Exception):
    pass


@dataclass
class NearbyStore:
    external_id: str  # "node/1234" o "way/1234" — id de OSM, no de ninguna cadena
    name: str
    brand: str | None
    lat: float
    lon: float


def fetch_nearby_supermarkets(lat: float, lon: float, radius_m: int = 3000) -> list[NearbyStore]:
    query = (
        "[out:json][timeout:20];"
        f'(node["shop"="supermarket"](around:{radius_m},{lat},{lon});'
        f'way["shop"="supermarket"](around:{radius_m},{lat},{lon}););'
        "out center;"
    )

    last_error: Exception | None = None
    resp = None
    for attempt in range(_MAX_RETRIES):
        if attempt > 0:
            time.sleep(_BASE_DELAY_S * (2**attempt) + random.uniform(0, 0.5))
        try:
            resp = httpx.post(
                settings.overpass_url,
                data={"data": query},
                # Verificado a mano: el Apache de Overpass devuelve 406 si el
                # User-Agent imita un navegador (ej. "Mozilla/5.0 (...)") —
                # rechaza precisamente lo que parece un scraper camuflado.
                # Identificarse honestamente como lo que es (una app real,
                # no un navegador) funciona sin problema.
                headers={
                    "User-Agent": "MercaChollo/1.0 (proyecto personal, sin fines comerciales)",
                    "Accept": "*/*",
                    "Accept-Encoding": "identity",
                },
                timeout=25.0,
            )
            resp.raise_for_status()
            break
        except httpx.HTTPError as exc:
            last_error = exc
            resp = None
    else:
        raise OverpassClientError(f"Overpass falló tras {_MAX_RETRIES} intentos: {last_error}")

    data = resp.json()
    stores: list[NearbyStore] = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue  # sin nombre no es útil para mostrar ni para emparejar cadena
        # los "way" (edificios) traen el centro en el campo "center", los "node" en lat/lon directo
        el_lat = el.get("lat") or el.get("center", {}).get("lat")
        el_lon = el.get("lon") or el.get("center", {}).get("lon")
        if el_lat is None or el_lon is None:
            continue
        stores.append(
            NearbyStore(
                external_id=f"{el['type']}/{el['id']}",
                name=name,
                brand=tags.get("brand"),
                lat=el_lat,
                lon=el_lon,
            )
        )
    return stores
