"""Cliente para precios reales de Lidl España vía Open Prices (proyecto
hermano de OpenFoodFacts, precios enviados por la comunidad).

Verificado en directo (agente `researcher` + comprobación manual): lidl.es
**sí tiene tienda online real** (Nuxt 3, JSON estructurado SSR), pero **solo
vende bazar/no-alimentación** — cero productos de comida en su navegación.
El enlace "Alimentación" redirige al folleto semanal, que a diferencia de
Aldi son **imágenes escaneadas** del catálogo en papel, no JSON — no hay
forma limpia de sacar el catálogo real.

Open Prices sí tiene datos reales de Lidl España, pero es un dataset disperso
enviado por usuarios (~100 precios en total, no un catálogo) — su filtrado
por API está roto de verdad (cualquier combinación de parámetros devuelve
siempre el mismo primer resultado sin filtrar, verificado en directo), así
que hay que paginar todas las ubicaciones (69 páginas de 100, tope real de
`size` pese a pedir más) y filtrar en cliente por país=ES y marca/nombre que
contenga "lidl".

**Limitación real y aceptada**: esto da cobertura puntual (si escaneas o
buscas justo uno de esos ~80-100 productos, aparece su precio real de Lidl)
pero no una alternativa comparable a un catálogo de verdad — se documenta así
a propósito, sin prometer más de lo que hay.
"""

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

_LOCATIONS_URL = "https://prices.openfoodfacts.org/api/v1/locations"
_PRICES_URL = "https://prices.openfoodfacts.org/api/v1/prices"
_HEADERS = {"User-Agent": "MercaChollo/1.0 (proyecto personal, sin fines comerciales)"}
_PAGE_SIZE = 100  # tope real de la API pese a pedir un size mayor


class LidlClientError(Exception):
    pass


@dataclass
class LidlProduct:
    external_id: str  # EAN real del producto
    name: str
    top_category: str
    category: str
    unit: str | None
    price: float
    image_url: str | None


def _is_lidl_spain(location: dict) -> bool:
    if location.get("osm_address_country_code") != "ES":
        return False
    brand = (location.get("osm_brand") or "").lower()
    name = (location.get("osm_name") or "").lower()
    return "lidl" in brand or "lidl" in name


def _fetch_lidl_location_ids() -> list[int]:
    ids: list[int] = []
    page = 1
    while True:
        resp = httpx.get(
            _LOCATIONS_URL, params={"page": page, "size": _PAGE_SIZE}, headers=_HEADERS, timeout=15.0
        )
        resp.raise_for_status()
        data = resp.json()
        ids.extend(loc["id"] for loc in data["items"] if _is_lidl_spain(loc))
        if page >= data["pages"]:
            break
        page += 1
    return ids


def _category_from_tags(product: dict) -> str:
    tags = product.get("categories_tags") or []
    if not tags:
        return "Otros"
    # tags vienen como "en:dairies", "es:jamon-curado" — nos quedamos con la
    # parte más específica (última) legible, sin prefijo de idioma.
    label = tags[-1].split(":", 1)[-1].replace("-", " ")
    return label.capitalize()


def fetch_lidl_products() -> list[LidlProduct]:
    try:
        location_ids = _fetch_lidl_location_ids()
    except httpx.HTTPError as exc:
        raise LidlClientError(f"Fallo listando tiendas Lidl en Open Prices: {exc}") from exc

    products: dict[str, LidlProduct] = {}
    for location_id in location_ids:
        try:
            resp = httpx.get(
                _PRICES_URL,
                params={"location_id": location_id, "size": _PAGE_SIZE},
                headers=_HEADERS,
                timeout=15.0,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Open Prices falló para location_id %s: %s", location_id, exc)
            continue

        for item in resp.json().get("items", []):
            code = item.get("product_code")
            price = item.get("price")
            product = item.get("product") or {}
            name = (product.get("product_name") or "").strip()
            if not code or not name or price is None:
                continue
            top_category = _category_from_tags(product)
            products[code] = LidlProduct(
                external_id=code,
                name=name,
                top_category=top_category,
                category=top_category,
                unit=product.get("product_quantity_unit"),
                price=float(price),
                image_url=product.get("image_url"),
            )

    return list(products.values())
