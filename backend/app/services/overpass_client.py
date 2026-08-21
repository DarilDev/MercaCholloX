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

Además (verificado en producción, agosto 2026): Render (plan gratuito)
reparte IPs de salida compartidas entre todos sus clientes de la región —
si otro proyecto agota la cuota de Overpass, la IP compartida queda
limitada para todos, incluidos nosotros, sin que sea culpa de nuestro
propio tráfico. Por eso `settings.overpass_urls` es una lista, no una única
URL: si la primera está limitada/caída, se prueba la siguiente antes de
rendirse. Ningún mirror individual tiene garantía de servicio, así que esto
es solo mitigación, no una solución perfecta.
"""

import logging
import random
import time
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Verificado en producción (agosto 2026): un 429/504 sostenido por límite de
# cuota no se arregla reintentando la misma URL a los pocos segundos (Overpass
# exige una pausa de 30s tras un 429) — con varias URLs de respaldo en la
# lista, probar la siguiente URL vale más que insistir en la misma. Un único
# intento por URL, con timeout corto, para no acumular varios minutos de
# espera si fallan varias seguidas.
_MAX_RETRIES_PER_URL = 1
_BASE_DELAY_S = 1.5
_TIMEOUT_S = 12.0


class OverpassClientError(Exception):
    pass


@dataclass
class NearbyStore:
    external_id: str  # "node/1234" o "way/1234" — id de OSM, no de ninguna cadena
    name: str
    brand: str | None
    lat: float
    lon: float


def _post_to(url: str, query: str) -> httpx.Response | None:
    """Prueba una única URL de Overpass con reintento+backoff corto. Devuelve
    None (nunca lanza) si esa URL en concreto falla — quien llama decide si
    pasar a la siguiente URL de la lista."""
    for attempt in range(_MAX_RETRIES_PER_URL):
        if attempt > 0:
            time.sleep(_BASE_DELAY_S * (2**attempt) + random.uniform(0, 0.5))
        try:
            resp = httpx.post(
                url,
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
                timeout=_TIMEOUT_S,
            )
            resp.raise_for_status()
            return resp
        except httpx.HTTPError as exc:
            logger.warning("Overpass (%s) falló intento %d: %s", url, attempt + 1, exc)
    return None


def fetch_nearby_supermarkets(lat: float, lon: float, radius_m: int = 3000) -> list[NearbyStore]:
    query = (
        "[out:json][timeout:20];"
        f'(node["shop"="supermarket"](around:{radius_m},{lat},{lon});'
        f'way["shop"="supermarket"](around:{radius_m},{lat},{lon}););'
        "out center;"
    )

    resp = None
    for url in settings.overpass_urls:
        resp = _post_to(url, query)
        if resp is not None:
            break
    if resp is None:
        raise OverpassClientError(
            f"Overpass falló en las {len(settings.overpass_urls)} URLs configuradas"
        )

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
