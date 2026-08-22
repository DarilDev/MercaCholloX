from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Identidad anónima por dispositivo (header X-Device-Id), no login real.
    Suficiente para aislar los datos de un grupo de confianza (amigos/familia)
    entre sí — no es seguridad frente a un adversario. Ver docs/DECISIONS.md."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_uuid: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Store(Base):
    __tablename__ = "stores"
    __table_args__ = (UniqueConstraint("chain", "external_id", name="uq_store_chain_external_id"),)

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
    __table_args__ = (UniqueConstraint("chain", "external_id", name="uq_product_chain_external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    chain: Mapped[str] = mapped_column(String, index=True)
    external_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    top_category: Mapped[str | None] = mapped_column(String, nullable=True)  # "pasillo" tal cual lo llama la cadena
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # subcategoría dentro del pasillo
    # Pasillo común entre cadenas (ver services/category_mapping.py) — ej.
    # "Charcutería y quesos" agrupa el "Charcutería" + "Quesos" separados de
    # Dia junto con el "Charcutería y quesos" de Mercadona. Es lo que se usa
    # para navegar; top_category/category quedan como dato crudo de origen.
    canonical_category: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    # Materializado por el worker de refresco al escribir — evita recalcular
    # MAX(id) sobre `prices` (que crece sin límite) en cada lectura. `prices`
    # sigue existiendo tal cual para el histórico completo, esto es solo "cuál
    # es el precio ahora mismo".
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_price_captured_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class FuelStation(Base):
    """Cacheada desde el MITECO (ver services/miteco_client.py) — nunca se
    consulta en vivo por petición de usuario, se refresca a diario."""

    __tablename__ = "fuel_stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    gasoleo_a: Mapped[float | None] = mapped_column(Float, nullable=True)
    gasolina_95_e5: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    query: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    # Solo se rellena si el usuario tocó una sugerencia real al añadirlo (ver
    # ShoppingListScreen._pickSuggestion) — nunca se adivina a partir del
    # texto libre, si es null se muestra el icono genérico sin más.
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)


class ScanHistoryEntry(Base):
    """Registro de cada escaneo con datos reales de OpenFoodFacts — para
    poder añadirlo a la lista más tarde sin volver a escanear (ver Favorite
    para la lista de la compra en sí; esto es solo el historial)."""

    __tablename__ = "scan_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    ean: Mapped[str] = mapped_column(String)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    nutriscore_grade: Mapped[str | None] = mapped_column(String, nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class UserProfile(Base):
    """Una fila por usuario (antes era una fila única id=1 para toda la beta)."""

    __tablename__ = "user_profile"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    home_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    home_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    usual_store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    vehicle_consumption_l_per_100km: Mapped[float] = mapped_column(Float, default=6.5)
    fuel_type: Mapped[str] = mapped_column(String, default="gasoleo_a")
    hourly_value_eur: Mapped[float] = mapped_column(Float, default=8.0)
