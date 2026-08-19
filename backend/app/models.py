from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    chain: Mapped[str] = mapped_column(String, index=True)  # "mercadona", "dia" (fase 4)
    external_id: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String, nullable=True)
    wh_id: Mapped[str | None] = mapped_column(String, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    chain: Mapped[str] = mapped_column(String, index=True)
    external_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    top_category: Mapped[str | None] = mapped_column(String, index=True, nullable=True)  # "pasillo" (ej. Lácteos)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # subcategoría dentro del pasillo
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)


class Price(Base):
    """Append-only: cada consulta inserta una fila nueva, nunca se actualiza.
    Así el histórico de precios sale gratis desde el diseño inicial."""

    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    price: Mapped[float] = mapped_column(Float)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Favorite(Base):
    """Un artículo genérico de la lista de la compra habitual (ej. "leche entera"),
    no un producto de una cadena concreta — así se puede comparar el mismo
    artículo entre supermercados distintos buscando el producto más barato que
    encaje en cada cadena (ver services/shopping_list.py)."""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer, default=1)


class UserProfile(Base):
    """Fila única (id=1) mientras la beta sea de un solo usuario por backend."""

    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    home_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    usual_store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    vehicle_consumption_l_per_100km: Mapped[float] = mapped_column(Float, default=6.5)
    fuel_type: Mapped[str] = mapped_column(String, default="gasoleo_a")
    hourly_value_eur: Mapped[float] = mapped_column(Float, default=8.0)
