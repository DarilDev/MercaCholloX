"""Cliente para la API GraphQL pública (Magento, sin autenticación) de
hiperdino.es.

Verificado a mano (agente `researcher`, no de memoria): a diferencia de Dia
(Akamai) y Alcampo (AWS WAF, bloquea a la 2ª/3ª petición seguida), hiperdino.es
no tiene protección anti-bot delante — 5 búsquedas seguidas sin pausa
devolvieron 200 sin señal de rate-limit. La cabecera `x-magento-tags: FPC`
confirma que es una tienda Magento estándar.

Endpoint real:
  POST https://www.hiperdino.es/graphql
  Body: {"query": "query { products(search: \"...\", pageSize: 100) { ... } }"}

Igual que Dia, no se encontró un árbol de categorías navegable vía GraphQL
(`categoryList` con el id raíz devolvió vacío) — se puebla buscando por una
lista de términos habituales. A diferencia de Dia, cada producto SÍ trae su
propia jerarquía de categorías reales en la respuesta (`categories`), así que
el pasillo también sale gratis: se usa el nivel 2 (el nivel 1 es la raíz del
catálogo, no un pasillo real).
"""

import random
import time
from dataclasses import dataclass

import httpx

_MAX_RETRIES = 3
_BASE_DELAY_S = 1.5

_GRAPHQL_URL = "https://www.hiperdino.es/graphql"
_PAGE_SIZE = 100

# Misma lista que dia_client.SEARCH_TERMS — sustituye a un árbol de
# categorías que no hemos encontrado navegable en hiperdino.es.
SEARCH_TERMS = [
    "leche", "huevos", "mantequilla", "queso", "yogur", "pan", "arroz",
    "pasta", "aceite de oliva", "vinagre", "sal", "azúcar", "harina",
    "tomate", "cebolla", "ajo", "patata", "fruta", "verdura", "pollo",
    "carne picada", "jamón", "atún", "salmón", "legumbres", "cereales",
    "galletas", "chocolate", "café", "té", "agua", "refresco", "cerveza",
    "vino", "zumo", "papel higiénico", "detergente", "lavavajillas",
    "champú", "gel de ducha", "pañales",
]

_QUERY = """
query Search($term: String!, $pageSize: Int!) {
  products(search: $term, pageSize: $pageSize) {
    items {
      sku
      name
      categories { name level }
      price_range { minimum_price { regular_price { value } } }
      image { url }
    }
  }
}
"""


class HiperdinoClientError(Exception):
    pass


class HiperdinoBlockedError(HiperdinoClientError):
    """Bloqueo/límite — no reintentar, igual que con Dia/Mercadona."""


@dataclass
class HiperdinoProduct:
    external_id: str
    name: str
    top_category: str
    category: str
    unit: str | None
    price: float
    image_url: str | None


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }


def _categories(item: dict) -> tuple[str, str]:
    cats = sorted(
        (c for c in item.get("categories") or [] if c.get("level", 0) >= 2),
        key=lambda c: c.get("level", 0),
    )
    if not cats:
        return "Sin categoría", "Sin categoría"
    top = cats[0].get("name") or "Sin categoría"
    detail = cats[-1].get("name") or top
    return top, detail


def search_products(term: str) -> list[HiperdinoProduct]:
    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        if attempt > 0:
            time.sleep(_BASE_DELAY_S * (2**attempt) + random.uniform(0, 0.5))
        try:
            resp = httpx.post(
                _GRAPHQL_URL,
                json={"query": _QUERY, "variables": {"term": term, "pageSize": _PAGE_SIZE}},
                headers=_headers(),
                timeout=15.0,
            )
        except httpx.TransportError as exc:
            last_error = exc
            continue

        if resp.status_code in (403, 429):
            raise HiperdinoBlockedError(f"HiperDino devolvió {resp.status_code} buscando '{term}' — no reintentar.")
        if resp.status_code >= 500:
            last_error = HiperdinoClientError(f"Error {resp.status_code} buscando '{term}'")
            continue
        if resp.status_code != 200:
            last_error = HiperdinoClientError(f"Error {resp.status_code} buscando '{term}'")
            continue

        try:
            data = resp.json()
        except ValueError:
            raise HiperdinoBlockedError(f"Respuesta no-JSON de HiperDino buscando '{term}' — probable bloqueo.")

        if "errors" in data:
            last_error = HiperdinoClientError(f"GraphQL error buscando '{term}': {data['errors']}")
            continue

        products: list[HiperdinoProduct] = []
        for item in data.get("data", {}).get("products", {}).get("items", []):
            price_range = item.get("price_range") or {}
            price = (
                price_range.get("minimum_price", {})
                .get("regular_price", {})
                .get("value")
            )
            if price is None:
                continue
            top_category, category = _categories(item)
            image = item.get("image") or {}
            products.append(
                HiperdinoProduct(
                    external_id=str(item.get("sku")),
                    name=item.get("name", ""),
                    top_category=top_category,
                    category=category,
                    unit=None,
                    price=float(price),
                    image_url=image.get("url"),
                )
            )
        return products

    raise HiperdinoClientError(f"Fallo tras {_MAX_RETRIES} intentos buscando '{term}': {last_error}")
