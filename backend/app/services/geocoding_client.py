"""Convierte una dirección escrita en texto a coordenadas — para fijar casa/
trabajo sin depender del GPS (ver mobile LocationScreen). Gratis, sin key.

Photon (komoot.io) y Nominatim (OpenStreetMap) verificados en directo con una
dirección real: ambos devuelven resultados correctos para "Avenida Los
Abrigos, Tenerife". Se prueba Photon primero — está pensado específicamente
para autocompletado ("search as you type") — y Nominatim como respaldo, mismo
criterio que overpass_client.py/osrm_client.py (IPs de salida compartidas en
Render, ningún servicio público individual es 100% fiable).

Detalle verificado: el parámetro `lang` de Photon solo acepta
default/de/en/fr — "es" devuelve un error 400. Se omite y se deja el idioma
por defecto (los nombres de calle ya vienen en español desde OSM).
"""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class GeocodingClientError(Exception):
    pass


@dataclass
class GeocodeResult:
    label: str
    lat: float
    lon: float


def _search_photon(q: str, limit: int) -> list[GeocodeResult] | None:
    try:
        resp = httpx.get(
            f"{settings.photon_url}/",
            params={"q": q, "limit": limit},
            headers={"User-Agent": "MercaChollo/1.0 (proyecto personal, sin fines comerciales)"},
            timeout=10.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Photon falló: %s", exc)
        return None

    results = []
    for feature in resp.json().get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates")
        if not coords or len(coords) != 2:
            continue
        street = " ".join(filter(None, [props.get("street"), props.get("housenumber")]))
        label = ", ".join(
            filter(
                None,
                [
                    street or props.get("name"),
                    props.get("district") or props.get("city"),
                    props.get("state"),
                ],
            )
        )
        results.append(GeocodeResult(label=label or q, lat=coords[1], lon=coords[0]))
    return results


def _search_nominatim(q: str, limit: int) -> list[GeocodeResult] | None:
    try:
        resp = httpx.get(
            f"{settings.nominatim_url}/search",
            params={"q": q, "format": "json", "limit": limit},
            headers={"User-Agent": "MercaChollo/1.0 (proyecto personal, sin fines comerciales)"},
            timeout=10.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Nominatim falló: %s", exc)
        return None

    return [
        GeocodeResult(label=item["display_name"], lat=float(item["lat"]), lon=float(item["lon"]))
        for item in resp.json()
    ]


def search(q: str, limit: int = 5) -> list[GeocodeResult]:
    for searcher in (_search_photon, _search_nominatim):
        results = searcher(q, limit)
        if results is not None:
            return results
    raise GeocodingClientError("Geocodificación falló en Photon y Nominatim")
