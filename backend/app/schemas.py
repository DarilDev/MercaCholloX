from pydantic import BaseModel, ConfigDict


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chain: str
    external_id: str
    name: str
    top_category: str | None
    category: str | None
    unit: str | None
    image_url: str | None
    price: float | None  # último precio cacheado, si existe


class CategoryOut(BaseModel):
    name: str
    chains: dict[str, int]  # cadena -> nº de productos cacheados en este pasillo


class FavoriteIn(BaseModel):
    query: str
    quantity: int = 1


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    quantity: int


class MatchedItemOut(BaseModel):
    favorite_id: int
    query: str
    quantity: int
    matched_product: ProductOut | None
    unit_price: float | None
    subtotal: float | None


class ChainTotalOut(BaseModel):
    chain: str
    items: list[MatchedItemOut]
    total: float
    missing: list[str]


class ShoppingComparisonOut(BaseModel):
    chains: list[ChainTotalOut]
    cheapest_chain: str | None


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chain: str
    name: str
    address: str | None
    lat: float
    lon: float
    distance_km: float


class UserProfileIn(BaseModel):
    home_lat: float | None = None
    home_lon: float | None = None
    work_lat: float | None = None
    work_lon: float | None = None
    usual_store_id: int | None = None
    vehicle_consumption_l_per_100km: float = 6.5
    fuel_type: str = "gasoleo_a"
    hourly_value_eur: float = 8.0


class UserProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    home_lat: float | None
    home_lon: float | None
    work_lat: float | None
    work_lon: float | None
    usual_store_id: int | None
    vehicle_consumption_l_per_100km: float
    fuel_type: str
    hourly_value_eur: float
