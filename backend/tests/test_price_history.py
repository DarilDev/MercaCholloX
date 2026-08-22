from datetime import datetime, timedelta

from app.services.price_history import PricePoint, discount_label

_NOW = datetime(2026, 8, 22, 12, 0, 0)


def _point(days_ago: int, price: float) -> PricePoint:
    return PricePoint(price=price, captured_at=_NOW - timedelta(days=days_ago))


def test_discount_label_sin_historico():
    assert discount_label([]) is None


def test_discount_label_un_solo_precio_no_es_suficiente():
    assert discount_label([_point(0, 1.0)]) is None


def test_discount_label_oferta_real():
    history = [_point(20, 1.0), _point(10, 1.0), _point(5, 1.0), _point(0, 0.8)]
    label = discount_label(history)
    assert label is not None
    assert "20%" in label


def test_discount_label_mismo_precio_de_siempre():
    history = [_point(20, 1.0), _point(10, 1.0), _point(0, 1.0)]
    assert discount_label(history) == "No es más barato que de costumbre"


def test_discount_label_mas_caro_que_de_costumbre():
    history = [_point(20, 1.0), _point(10, 1.0), _point(0, 1.2)]
    assert discount_label(history) == "No es más barato que de costumbre"


def test_discount_label_ignora_precios_fuera_de_la_ventana_de_30_dias():
    # un precio carísimo hace 90 días no debería inflar la media de referencia
    history = [_point(90, 100.0), _point(10, 1.0), _point(0, 0.98)]
    label = discount_label(history)
    assert label == "No es más barato que de costumbre"


def test_discount_label_umbral_no_cuenta_bajadas_minimas_como_oferta():
    # 2% más barato no debería marcarse como oferta real (umbral 5%)
    history = [_point(10, 1.0), _point(0, 0.98)]
    assert discount_label(history) == "No es más barato que de costumbre"
