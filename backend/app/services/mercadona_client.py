"""Cliente para la API pública (no oficial, sin autenticación) de tienda.mercadona.es.

Verificado a mano contra la API real:
  GET /api/categories/?lang=es&wh={wh}        -> árbol de categorías (2 niveles)
  GET /api/categories/{id}/?lang=es&wh={wh}   -> subcategorías + productos con precio

`wh` identifica el almacén/región de reparto (los precios de Mercadona son
prácticamente uniformes en toda España — ver docs/DECISIONS.md — así que el
valor de `wh` solo afecta disponibilidad, no precio, salvo excepciones puntuales).

Es la única fuente de datos real del producto — nunca paralelizar peticiones
"para ir más rápido": es exactamente la señal que detectan los sistemas
anti-bot y el camino más rápido a perder el acceso (ver docs/DECISIONS.md,
sección "Arquitectura para escalar" del plan).
"""

import random
import time
from dataclasses import dataclass

import httpx

from app.config import settings

_MAX_RETRIES = 3
_BASE_DELAY_S = 1.0


class MercadonaClientError(Exception):
    pass


class MercadonaBlockedError(MercadonaClientError):
    """429/403 — nos han limitado o bloqueado. No reintentar: el llamador debe
    parar el refresco entero y avisar, no seguir insistiendo contra el bloqueo."""


@dataclass
class MercadonaProduct:
    external_id: str
    name: str
    top_category: str
    category: str
    unit: str | None
    price: float
    image_url: str | None


def _parse_price(raw: str | float | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(str(raw).strip())
    except ValueError:
        return None


def _client(timeout: float = 10.0) -> httpx.Client:
    return httpx.Client(
        base_url=settings.mercadona_base_url,
        headers={"User-Agent": "Mozilla/5.0 (MercaChollo dev)"},
        timeout=timeout,
    )


def _get(path: str, params: dict) -> dict:
    """GET con reintento acotado para fallos transitorios, y sin reintento
    (falla ya) para 429/403 — no tiene sentido insistir contra un bloqueo."""
    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        if attempt > 0:
            # backoff exponencial + jitter: un ritmo perfectamente regular es
            # en sí mismo una señal de bot, y machacar justo tras un fallo
            # transitorio no ayuda a nadie.
            delay = _BASE_DELAY_S * (2**attempt) + random.uniform(0, 0.5)
            time.sleep(delay)

        try:
            with _client() as client:
                resp = client.get(path, params=params)
        except httpx.TransportError as exc:  # timeout, conexión rota, etc.
            last_error = exc
            continue

        if resp.status_code in (403, 429):
            raise MercadonaBlockedError(
                f"Mercadona devolvió {resp.status_code} en {path} — parece un bloqueo/límite, no reintentar."
            )
        if resp.status_code >= 500:
            last_error = MercadonaClientError(f"Error {resp.status_code} en {path}")
            continue

        resp.raise_for_status()  # otros 4xx: no es transitorio, no reintentar
        return resp.json()

    raise MercadonaClientError(f"Fallo tras {_MAX_RETRIES} intentos en {path}: {last_error}")


def fetch_category_tree(wh: str | None = None) -> list[dict]:
    """Devuelve el árbol de categorías top-level, cada una con sus subcategorías (id, name)."""
    wh = wh or settings.mercadona_default_wh
    data = _get("/categories/", {"lang": "es", "wh": wh})
    return data["results"]


def fetch_leaf_category_ids(wh: str | None = None) -> list[tuple[int, str, str]]:
    """Aplana el árbol y devuelve (id, nombre_subcategoria, nombre_pasillo) de cada
    subcategoría hoja — las que realmente contienen productos al consultarlas
    individualmente. El "pasillo" es la categoría top-level (ej. "Lácteos, huevos
    y sustitutos"), usado para navegar la app como un supermercado real."""
    tree = fetch_category_tree(wh)
    leaves: list[tuple[int, str, str]] = []
    for top in tree:
        for sub in top.get("categories", []):
            leaves.append((sub["id"], sub["name"], top["name"]))
    return leaves


def fetch_category_products(
    category_id: int, top_category: str, wh: str | None = None
) -> list[MercadonaProduct]:
    """Consulta una subcategoría y devuelve sus productos con precio, imagen y pasillo."""
    wh = wh or settings.mercadona_default_wh
    data = _get(f"/categories/{category_id}/", {"lang": "es", "wh": wh})

    products: list[MercadonaProduct] = []
    for group in data.get("categories", []):
        group_name = group.get("name", data.get("name", ""))
        for raw in group.get("products", []):
            price_instructions = raw.get("price_instructions", {})
            price = _parse_price(price_instructions.get("unit_price"))
            if price is None:
                continue
            products.append(
                MercadonaProduct(
                    external_id=str(raw["id"]),
                    name=raw.get("display_name", raw.get("slug", "")),
                    top_category=top_category,
                    category=group_name,
                    unit=price_instructions.get("unit_name"),
                    price=price,
                    image_url=raw.get("thumbnail"),
                )
            )
    return products
