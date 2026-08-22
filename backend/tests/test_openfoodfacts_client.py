import pytest

from app.services.openfoodfacts_client import _parse_product, get_product

_COCA_COLA_EAN = "5449000034298"  # verificado en directo (ver plan)


def test_parse_product_normaliza_grade_a_mayuscula():
    data = {
        "status": 1,
        "product": {
            "product_name": "Coca-Cola Original",
            "image_url": "https://example.com/img.jpg",
            "nutriscore_grade": "d",
            "nova_group": 4,
            "additives_tags": ["en:e150d", "en:e338"],
        },
    }
    result = _parse_product(_COCA_COLA_EAN, data)
    assert result.name == "Coca-Cola Original"
    assert result.nutriscore_grade == "D"
    assert result.nova_group == 4
    assert result.additives_count == 2


def test_parse_product_sin_datos_opcionales():
    result = _parse_product("123", {"status": 1, "product": {}})
    assert result.name is None
    assert result.image_url is None
    assert result.nutriscore_grade is None
    assert result.nova_group is None
    assert result.additives_count == 0


@pytest.mark.live
def test_get_product_ean_real():
    product = get_product(_COCA_COLA_EAN)
    assert product is not None
    assert product.name is not None
    assert product.nutriscore_grade is not None


@pytest.mark.live
def test_get_product_ean_inexistente_devuelve_none():
    assert get_product("0000000000000") is None
