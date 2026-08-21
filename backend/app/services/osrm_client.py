"""Cliente para el servidor demo público de OSRM — distancia y tiempo reales
de conducción entre dos puntos (no línea recta). Gratis, sin key.

Nota: es un servidor de demo/pruebas, no pensado para tráfico de producción
alto — aceptable para una beta de amigos con pocas consultas puntuales; ver
docs/DECISIONS.md, "Arquitectura para escalar" (autoalojar si el uso deja de
ser ocasional).

Igual que Overpass (ver overpass_client.py): Render reparte IPs de salida
compartidas, así que `settings.osrm_urls` es una lista con respaldo, no una
única URL — si el servidor demo principal falla, se prueba el de FOSSGIS
antes de rendirse.
"""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OsrmClientError(Exception):
    pass


@dataclass
class Route:
    distance_km: float
    duration_min: float


def _get_from(base_url: str, path: str) -> httpx.Response | None:
    try:
        resp = httpx.get(f"{base_url}{path}", params={"overview": "false"}, timeout=15.0)
        resp.raise_for_status()
        return resp
    except httpx.HTTPError as exc:
        logger.warning("OSRM (%s) falló: %s", base_url, exc)
        return None


def route(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> Route:
    path = f"/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}"

    resp = None
    for base_url in settings.osrm_urls:
        resp = _get_from(base_url, path)
        if resp is not None:
            break
    if resp is None:
        raise OsrmClientError(f"OSRM falló en las {len(settings.osrm_urls)} URLs configuradas")

    data = resp.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise OsrmClientError(f"OSRM no encontró ruta: {data.get('code')}")

    best = data["routes"][0]
    return Route(
        distance_km=round(best["distance"] / 1000, 2),
        duration_min=round(best["duration"] / 60, 1),
    )
