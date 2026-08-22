"""Historial de precios — la tabla `prices` es append-only desde el diseño
inicial (ver models.py), así que este dato sale gratis sin worker nuevo.

`discount_label` es una función pura (recibe el histórico ya cargado, no
toca la base de datos) — mismo criterio que scoring.py: un error de signo
aquí mostraría "es una oferta real" cuando no lo es, de forma silenciosa,
así que se testea sin red ni mocks complicados.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Price

_DISCOUNT_WINDOW_DAYS = 30
_DISCOUNT_THRESHOLD = 0.05  # 5% más barato que la media para contar como oferta real


@dataclass
class PricePoint:
    price: float
    captured_at: datetime


def get_history(db: Session, product_id: int) -> list[PricePoint]:
    rows = (
        db.query(Price)
        .filter(Price.product_id == product_id)
        .order_by(Price.captured_at)
        .all()
    )
    return [PricePoint(price=r.price, captured_at=r.captured_at) for r in rows]


def discount_label(history: list[PricePoint]) -> str | None:
    """None si no hay histórico suficiente para opinar (menos de 2 puntos:
    un único precio no puede compararse consigo mismo)."""
    if len(history) < 2:
        return None

    current = history[-1]
    window_start = current.captured_at - timedelta(days=_DISCOUNT_WINDOW_DAYS)
    # la media de los días previos, sin contar el precio actual — si no, el
    # propio precio actual "diluye" la comparación contra sí mismo
    window_prices = [p.price for p in history[:-1] if p.captured_at >= window_start]
    if not window_prices:
        return None

    avg = sum(window_prices) / len(window_prices)
    if avg <= 0:
        return None

    diff_ratio = (avg - current.price) / avg
    if diff_ratio >= _DISCOUNT_THRESHOLD:
        return f"▼ {round(diff_ratio * 100)}% más barato que la media de {_DISCOUNT_WINDOW_DAYS} días"
    return "No es más barato que de costumbre"
