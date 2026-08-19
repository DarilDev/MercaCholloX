from app.services.mercadona_client import _parse_price, fetch_category_products


def test_parse_price_handles_normal_value():
    assert _parse_price("3.80") == 3.80


def test_parse_price_handles_fixed_width_quirk():
    # La API real de Mercadona a veces devuelve previous_unit_price con
    # espacios de relleno, ej. "        3.95" — visto en producción.
    assert _parse_price("        3.95") == 3.95


def test_parse_price_handles_none():
    assert _parse_price(None) is None


def test_fetch_category_products_normalizes_real_category():
    # Golpea la API real de Mercadona (categoría hoja "Refresco de cola",
    # id devuelto por fetch_leaf_category_ids) — confirma que el parser sigue
    # encajando con el formato real, no solo con datos mockeados.
    products = fetch_category_products(158, top_category="Agua y refrescos")
    assert len(products) > 0
    assert all(p.price > 0 for p in products)
    assert all(p.external_id for p in products)
