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
    subcategories: list[str]


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
