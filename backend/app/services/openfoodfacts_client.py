"""Consulta OpenFoodFacts por código de barras (EAN) para el escáner de
salud estilo Yuka.

Verificado en directo: el lookup por EAN individual funciona rápido y fiable
incluso cuando la búsqueda general de OpenFoodFacts (`cgi/search.pl`) está
degradada — irrelevante para este caso de uso porque escanear siempre da un
EAN exacto, nunca hace falta buscar por texto. Lidl tiene presencia real en
OpenFoodFacts (miles de productos indexados), así que esto no se limita a
las cadenas ya integradas en la app.
"""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OpenFoodFactsError(Exception):
    pass


@dataclass
class OffProduct:
    ean: str
    name: str | None
    image_url: str | None
    nutriscore_grade: str | None
    nova_group: int | None
    additives_count: int


def _parse_product(ean: str, data: dict) -> OffProduct:
    product = data.get("product") or {}
    grade = (product.get("nutriscore_grade") or "").upper()
    return OffProduct(
        ean=ean,
        name=product.get("product_name") or None,
        image_url=product.get("image_url") or None,
        nutriscore_grade=grade or None,
        nova_group=product.get("nova_group"),
        additives_count=len(product.get("additives_tags") or []),
    )


def get_product(ean: str) -> OffProduct | None:
    """None si el EAN no existe en OpenFoodFacts (respuesta válida, sin
    producto). Lanza OpenFoodFactsError si el propio servicio falla."""
    try:
        resp = httpx.get(
            f"{settings.openfoodfacts_url}/{ean}.json",
            headers={"User-Agent": "MercaChollo/1.0 (proyecto personal, sin fines comerciales)"},
            timeout=10.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("OpenFoodFacts falló para EAN %s: %s", ean, exc)
        raise OpenFoodFactsError(str(exc)) from exc

    data = resp.json()
    if data.get("status") != 1:
        return None
    return _parse_product(ean, data)
