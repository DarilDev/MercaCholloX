"""Cliente para el folleto de ofertas semanales de aldi.es (sin API, sin
autenticación).

Verificado a mano (agente `researcher`): Aldi España **no tiene tienda
online** — `buscar.html`, `carrito.html`, `tienda-online.html` devuelven 404,
y la propia web lo confirma en su FAQ de ofertas ("Actualmente no es posible
reservar productos en la web"). La única fuente de precio real es la página
de ofertas de la semana, pero NO es una imagen escaneada: Next.js incrusta el
catálogo completo como JSON en `<script id="__NEXT_DATA__">`.

  GET https://www.aldi.es/ofertas.html   (HTML normal, sin headers especiales)
  → __NEXT_DATA__.props.pageProps.apiData   (string JSON, un solo nivel)
  → next(payload for name, payload in json.loads(apiData) if name == "OFFER_GET")
  → .res.algoliaDataMap   (dict id → producto)

No es un endpoint API parametrizable de verdad: todo se resuelve
server-side en el SSR de Next.js, así que "consumirlo" es pedir el HTML y
parsear ese script — no hay forma de buscar por término, solo se obtiene lo
que esté en oferta esta semana (~90 productos de alimentación, mezclados con
~80 de bazar/textil/jardín que se descartan).

**Limitación real, a diferencia de Mercadona/Dia/HiperDino**: esto no es un
catálogo permanente, es un folleto — solo cubre productos en oferta la
semana en curso. Un producto que deja de estar en oferta no se vuelve a
tocar (se queda con su último precio conocido, igual que si Aldi dejara de
responder), no hay forma de "buscar" el resto del catálogo de Aldi.

Filtrado a alimentación: los productos de bazar/oficina/jardín/juguetes
tienen `mainCategoryID=None` en la respuesta real (verificado: mochilas,
plantas, folios, coches de juguete...) — los productos de alimentación
siempre lo tienen. `hierarchicalCategories.lvl0` mezcla pasillos reales con
colecciones de marketing ("Verano", "Marcas") — se descartan esas etiquetas
conocidas al elegir el pasillo.
"""

import json
import re
from dataclasses import dataclass

import httpx

_OFFERS_URL = "https://www.aldi.es/ofertas.html"
_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S
)
_MARKETING_LABELS = {"verano", "marcas", "novedades", "ofertas", "destacados"}


class AldiClientError(Exception):
    pass


class AldiBlockedError(AldiClientError):
    """Bloqueo/límite — no reintentar, igual que con Dia/HiperDino."""


@dataclass
class AldiProduct:
    external_id: str
    name: str
    top_category: str
    category: str
    unit: str | None
    price: float
    image_url: str | None


def _top_category(item: dict) -> str:
    for label in item.get("hierarchicalCategories", {}).get("lvl0", []):
        if label.strip().lower() not in _MARKETING_LABELS:
            return label
    main_id = item.get("mainCategoryID") or "sin-categoria"
    return main_id.replace("-", " ").capitalize()


def _category(item: dict, top_category: str) -> str:
    lvl1 = item.get("hierarchicalCategories", {}).get("lvl1", [])
    if lvl1:
        # Formato real: "Pasillo > Sub-pasillo" — nos quedamos con la parte
        # después del último ">" si la tiene.
        return lvl1[0].rsplit(">", 1)[-1].strip()
    return top_category


def _image_url(item: dict) -> str | None:
    assets = item.get("assets") or []
    primary = next((a for a in assets if a.get("type") == "primary"), None)
    return (primary or assets[0]).get("url") if (primary or assets) else None


def _clean_name(item: dict) -> str:
    brand = (item.get("brandName") or "").replace("®", "").strip()
    name = (item.get("name") or "").strip()
    return f"{brand} {name}".strip() if brand else name


def fetch_offers() -> list[AldiProduct]:
    try:
        resp = httpx.get(_OFFERS_URL, timeout=15.0)
    except httpx.TransportError as exc:
        raise AldiClientError(f"Fallo de red pidiendo el folleto de Aldi: {exc}") from exc

    if resp.status_code in (403, 429):
        raise AldiBlockedError(f"Aldi devolvió {resp.status_code} pidiendo el folleto — no reintentar.")
    if resp.status_code != 200:
        raise AldiClientError(f"Error {resp.status_code} pidiendo el folleto de Aldi")

    match = _NEXT_DATA_RE.search(resp.text)
    if not match:
        raise AldiBlockedError("No se encontró __NEXT_DATA__ en la página de ofertas — probable cambio de web/bloqueo.")

    try:
        next_data = json.loads(match.group(1))
        api_data = json.loads(next_data["props"]["pageProps"]["apiData"])
        offer_payload = next(payload for name, payload in api_data if name == "OFFER_GET")
        data_map = offer_payload["res"]["algoliaDataMap"]
    except (ValueError, KeyError, StopIteration, TypeError) as exc:
        raise AldiClientError(f"Estructura inesperada en __NEXT_DATA__ de Aldi: {exc}") from exc

    products: list[AldiProduct] = []
    for object_id, item in data_map.items():
        if item.get("mainCategoryID") is None:
            continue  # bazar/textil/jardín/juguetes, no es alimentación
        price = item.get("currentPrice", {}).get("priceValue")
        if price is None:
            continue
        top_category = _top_category(item)
        products.append(
            AldiProduct(
                external_id=str(object_id),
                name=_clean_name(item),
                top_category=top_category,
                category=_category(item, top_category),
                unit=item.get("salesUnit"),
                price=float(price),
                image_url=_image_url(item),
            )
        )
    return products
