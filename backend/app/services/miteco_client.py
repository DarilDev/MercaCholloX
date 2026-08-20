"""Cliente para el Geoportal de Hidrocarburos del MITECO — precio real de
combustible en ~11.000 gasolineras de España. Gratis, sin key.

Verificado a mano contra la API real:
  GET https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/

Dos detalles reales del formato, no documentados en ningún sitio que se haya
encontrado, solo viendo la respuesta real:
- Los precios vienen como texto con **coma decimal** ("1,789"), no punto.
- Un combustible que la estación no vende llega como **string vacío** (""),
  no como null — hay que tratarlo como "no disponible", no como 0€.

Respuesta completa >10MB (todo el país junto, sin filtro por zona en este
endpoint) — se cachea en `FuelStation` vía workers/refresh_fuel_prices.py,
nunca se pide en vivo por petición de usuario.
"""

from dataclasses import dataclass

import httpx

from app.config import settings


class MitecoClientError(Exception):
    pass


@dataclass
class FuelStationPrice:
    external_id: str  # "IDEESS"
    name: str  # "Rótulo"
    lat: float
    lon: float
    gasoleo_a: float | None
    gasolina_95_e5: float | None


def _parse_price(raw: str) -> float | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def _parse_coord(raw: str) -> float | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def fetch_all_stations() -> list[FuelStationPrice]:
    try:
        resp = httpx.get(
            settings.miteco_url,
            headers={"User-Agent": "MercaChollo/1.0 (proyecto personal, sin fines comerciales)"},
            timeout=60.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise MitecoClientError(f"Error consultando MITECO: {exc}") from exc

    data = resp.json()
    stations: list[FuelStationPrice] = []
    for raw in data.get("ListaEESSPrecio", []):
        lat = _parse_coord(raw.get("Latitud", ""))
        lon = _parse_coord(raw.get("Longitud (WGS84)", ""))
        if lat is None or lon is None:
            continue
        stations.append(
            FuelStationPrice(
                external_id=raw.get("IDEESS", ""),
                name=raw.get("Rótulo", ""),
                lat=lat,
                lon=lon,
                gasoleo_a=_parse_price(raw.get("Precio Gasoleo A", "")),
                gasolina_95_e5=_parse_price(raw.get("Precio Gasolina 95 E5", "")),
            )
        )
    return stations
