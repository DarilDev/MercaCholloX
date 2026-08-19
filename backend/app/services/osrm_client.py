"""Cliente para el servidor demo público de OSRM — distancia y tiempo reales
de conducción entre dos puntos (no línea recta). Gratis, sin key.

Nota: es un servidor de demo/pruebas, no pensado para tráfico de producción
alto — aceptable para una beta de amigos con pocas consultas puntuales; ver
docs/DECISIONS.md, "Arquitectura para escalar" (autoalojar si el uso deja de
ser ocasional).
"""

from dataclasses import dataclass

import httpx

from app.config import settings


class OsrmClientError(Exception):
    pass


@dataclass
class Route:
    distance_km: float
    duration_min: float


def route(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> Route:
    path = f"/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}"
    try:
        resp = httpx.get(
            f"{settings.osrm_url}{path}", params={"overview": "false"}, timeout=15.0
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise OsrmClientError(f"Error consultando OSRM: {exc}") from exc

    data = resp.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise OsrmClientError(f"OSRM no encontró ruta: {data.get('code')}")

    best = data["routes"][0]
    return Route(
        distance_km=round(best["distance"] / 1000, 2),
        duration_min=round(best["duration"] / 60, 1),
    )
