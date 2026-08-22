import pytest

from app.services.lidl_client import _category_from_tags, _is_lidl_spain, fetch_lidl_products


def test_is_lidl_spain_true_con_brand():
    assert _is_lidl_spain({"osm_address_country_code": "ES", "osm_brand": "Lidl"}) is True


def test_is_lidl_spain_false_otro_pais():
    assert _is_lidl_spain({"osm_address_country_code": "FR", "osm_brand": "Lidl"}) is False


def test_is_lidl_spain_false_otra_marca():
    assert _is_lidl_spain({"osm_address_country_code": "ES", "osm_brand": "Mercadona"}) is False


def test_category_from_tags_sin_tags():
    assert _category_from_tags({}) == "Otros"


def test_category_from_tags_limpia_prefijo():
    assert _category_from_tags({"categories_tags": ["en:dairies", "es:jamon-curado"]}) == "Jamon curado"


@pytest.mark.live
def test_fetch_lidl_products_trae_precios_reales():
    # Golpea Open Prices real — confirma que sigue habiendo tiendas Lidl
    # España con precios reales enviados por la comunidad.
    # Ejecutar a mano con: pytest -m live (tarda ~1 min, pagina 69 páginas)
    products = fetch_lidl_products()
    assert len(products) > 0
    assert all(p.price > 0 for p in products)
    assert all(p.external_id for p in products)
