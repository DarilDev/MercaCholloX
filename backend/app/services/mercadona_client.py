"""Cliente para la API pública (no oficial, sin autenticación) de tienda.mercadona.es.

Verificado a mano contra la API real:
  GET /api/categories/?lang=es&wh={wh}        -> árbol de categorías (2 niveles)
  GET /api/categories/{id}/?lang=es&wh={wh}   -> subcategorías + productos con precio

`wh` identifica el almacén/región de reparto (los precios de Mercadona son
prácticamente uniformes en toda España — ver docs/DECISIONS.md — así que el
valor de `wh` solo afecta disponibilidad, no precio, salvo excepciones puntuales).
"""

from dataclasses import dataclass

import httpx

from app.config import settings


class MercadonaClientError(Exception):
    pass


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


def fetch_category_tree(wh: str | None = None) -> list[dict]:
    """Devuelve el árbol de categorías top-level, cada una con sus subcategorías (id, name)."""
    wh = wh or settings.mercadona_default_wh
    with _client() as client:
        resp = client.get("/categories/", params={"lang": "es", "wh": wh})
        resp.raise_for_status()
        data = resp.json()
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
    with _client() as client:
        resp = client.get(f"/categories/{category_id}/", params={"lang": "es", "wh": wh})
        resp.raise_for_status()
        data = resp.json()

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
