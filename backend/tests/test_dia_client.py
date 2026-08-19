import pytest

from app.services.dia_client import search_products


@pytest.mark.live
def test_search_products_returns_real_results():
    # Golpea la API real de Dia — confirma que el endpoint descubierto a mano
    # (/api/v1/search-back/search) sigue funcionando con headers generados
    # por nosotros. Ejecutar a mano con: pytest -m live
    products = search_products("leche")
    assert len(products) > 0
    assert all(p.price > 0 for p in products)
    assert all(p.external_id for p in products)
