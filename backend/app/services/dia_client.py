"""Cliente para la API pública (no oficial, sin autenticación) de dia.es.

Verificado a mano: Selenium (con y sin undetected-chromedriver) recibe
"Access Denied" de Akamai al cargar dia.es — coincide con lo documentado en
docs/DATA_SOURCES.md sobre otros scrapers necesitando navegador real. Pero
peticiones HTTP simples (httpx, sin ejecutar JS) SÍ pasan, así que no hace
falta Selenium/Chrome para esto — más ligero y más fiable.

Endpoint real descubierto inspeccionando la página de búsqueda embebida
(`vike_pageContext` → `endpoints.search.client`):
  GET https://www.dia.es/api/v1/search-back/search?q={term}
Necesita las cabeceras que la propia web manda (`cart_id`, `session_id`,
`customer_id`, `x-locale`) — verificado que aceptan valores generados por
nosotros (UUIDs propios), no hace falta arrastrar sesión de una carga previa
de la home.

A diferencia de Mercadona, dia.es no tiene un árbol de categorías navegable
descubierto — se puebla el catálogo buscando por una lista de términos
habituales de la compra. Cada resultado ya trae su categoría real de Dia
(`l1_category_description`/`l2_category_description`), así que el pasillo
sale gratis igualmente.
"""

import random
import time
import uuid
from dataclasses import dataclass

import httpx

_MAX_RETRIES = 3
_BASE_DELAY_S = 1.5

_SEARCH_URL = "https://www.dia.es/api/v1/search-back/search"
_IMAGE_BASE = "https://www.dia.es"

# Términos habituales de la compra — sustituye a un árbol de categorías que
# no hemos encontrado navegable en dia.es. Se puede ampliar con el tiempo.
SEARCH_TERMS = [
    "leche", "huevos", "mantequilla", "queso", "yogur", "pan", "arroz",
    "pasta", "aceite de oliva", "vinagre", "sal", "azúcar", "harina",
    "tomate", "cebolla", "ajo", "patata", "fruta", "verdura", "pollo",
    "carne picada", "jamón", "atún", "salmón", "legumbres", "cereales",
    "galletas", "chocolate", "café", "té", "agua", "refresco", "cerveza",
    "vino", "zumo", "papel higiénico", "detergente", "lavavajillas",
    "champú", "gel de ducha", "pañales",
]


class DiaClientError(Exception):
    pass


class DiaBlockedError(DiaClientError):
    """Bloqueo/límite — no reintentar, igual que con Mercadona/Overpass."""


@dataclass
class DiaProduct:
    external_id: str
    name: str
    top_category: str
    category: str
    unit: str | None
    price: float
    image_url: str | None


def _headers() -> dict:
    return {
        "Accept": "application/json, text/plain, */*",
        "cart_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "customer_id": "",
        "x-locale": "es",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }


def search_products(term: str) -> list[DiaProduct]:
    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        if attempt > 0:
            time.sleep(_BASE_DELAY_S * (2**attempt) + random.uniform(0, 0.5))
        try:
            resp = httpx.get(
                _SEARCH_URL, params={"q": term}, headers=_headers(), timeout=15.0
            )
        except httpx.TransportError as exc:
            last_error = exc
            continue

        if resp.status_code in (403, 429):
            raise DiaBlockedError(f"Dia devolvió {resp.status_code} buscando '{term}' — no reintentar.")
        if resp.status_code >= 500:
            last_error = DiaClientError(f"Error {resp.status_code} buscando '{term}'")
            continue
        if resp.status_code != 200:
            last_error = DiaClientError(f"Error {resp.status_code} buscando '{term}'")
            continue

        try:
            data = resp.json()
        except ValueError:
            # Respuesta no-JSON (ej. página de bloqueo de Akamai) — tratar
            # como bloqueo, no como fallo transitorio a reintentar.
            raise DiaBlockedError(f"Respuesta no-JSON de Dia buscando '{term}' — probable bloqueo.")

        products: list[DiaProduct] = []
        for item in data.get("search_items", []):
            prices = item.get("prices", {})
            price = prices.get("price")
            if price is None:
                continue
            image_path = item.get("image")
            products.append(
                DiaProduct(
                    external_id=str(item.get("object_id") or item.get("sku_id")),
                    name=item.get("display_name", ""),
                    top_category=item.get("l1_category_description") or "Sin categoría",
                    category=item.get("l2_category_description") or "Sin categoría",
                    unit=prices.get("measure_unit"),
                    price=float(price),
                    image_url=f"{_IMAGE_BASE}{image_path}" if image_path else None,
                )
            )
        return products

    raise DiaClientError(f"Fallo tras {_MAX_RETRIES} intentos buscando '{term}': {last_error}")
