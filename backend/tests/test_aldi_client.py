import pytest

from app.services.aldi_client import fetch_offers


@pytest.mark.live
def test_fetch_offers_returns_real_food_products():
    # Golpea la página real de ofertas de Aldi — confirma que el parseo del
    # __NEXT_DATA__ (OFFER_GET -> algoliaDataMap) sigue funcionando y que el
    # filtro de bazar/textil (mainCategoryID=None) deja solo alimentación.
    # Ejecutar a mano con: pytest -m live
    products = fetch_offers()
    assert len(products) > 0
    assert all(p.price > 0 for p in products)
    assert all(p.external_id for p in products)
    assert all(p.top_category.lower() not in {"verano", "marcas"} for p in products)
