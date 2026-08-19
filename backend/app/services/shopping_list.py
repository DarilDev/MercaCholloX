"""Compara la lista de la compra (favoritos) entre las cadenas cacheadas.

Cada favorito es un texto genérico (ej. "leche entera"), no un producto de una
cadena concreta. Para cada cadena, se busca el producto más barato cuyo nombre
contenga todas las palabras del texto — el mismo matching por substring que ya
usa /products/search, así el resultado es explicable: se muestra qué producto
concreto se emparejó, no una caja negra.
"""

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Favorite, Price, Product

_STOPWORDS = {
    "de", "del", "la", "el", "los", "las", "y", "en", "con", "sin", "para",
    "un", "una", "unos", "unas", "al", "a", "o",
}


@dataclass
class MatchedItem:
    favorite_id: int
    query: str
    quantity: int
    product: Product | None
    unit_price: float | None

    @property
    def subtotal(self) -> float | None:
        if self.unit_price is None:
            return None
        return round(self.unit_price * self.quantity, 2)


@dataclass
class ChainTotal:
    chain: str
    items: list[MatchedItem]

    @property
    def total(self) -> float:
        return round(sum(i.subtotal or 0.0 for i in self.items), 2)

    @property
    def missing(self) -> list[str]:
        return [i.query for i in self.items if i.product is None]


def _cheapest_match(db: Session, chain: str, query: str) -> tuple[Product, float] | None:
    words = [w for w in query.strip().lower().split() if w and w not in _STOPWORDS]
    if not words:
        return None

    latest_price_ids = (
        db.query(Price.product_id, func.max(Price.id).label("latest_id"))
        .group_by(Price.product_id)
        .subquery()
    )
    q = (
        db.query(Product, Price.price)
        .join(latest_price_ids, Product.id == latest_price_ids.c.product_id)
        .join(Price, Price.id == latest_price_ids.c.latest_id)
        .filter(Product.chain == chain)
    )
    for word in words:
        q = q.filter(Product.name.ilike(f"%{word}%"))

    candidates = q.all()
    if not candidates:
        return None

    # "Más barato que encaje" por sí solo falla: un tarrito de tomate que
    # menciona "aceite de oliva" en su nombre le gana en precio a una botella
    # de aceite de verdad. Se prioriza el nombre más "cercano" a la búsqueda
    # (menos palabras de más) y solo se usa el precio como desempate — así un
    # producto que es literalmente lo buscado gana sobre uno que solo lo menciona.
    def noise(product: Product) -> int:
        name_words = len(product.name.lower().split())
        return max(name_words - len(words), 0)

    candidates.sort(key=lambda pair: (noise(pair[0]), pair[1]))
    return candidates[0]


def known_chains(db: Session) -> list[str]:
    return [row[0] for row in db.query(Product.chain).distinct().all()]


def compare_favorites(db: Session) -> list[ChainTotal]:
    favorites = db.query(Favorite).all()
    results: list[ChainTotal] = []

    for chain in known_chains(db):
        items: list[MatchedItem] = []
        for fav in favorites:
            match = _cheapest_match(db, chain, fav.query)
            if match:
                product, price = match
                items.append(
                    MatchedItem(
                        favorite_id=fav.id,
                        query=fav.query,
                        quantity=fav.quantity,
                        product=product,
                        unit_price=price,
                    )
                )
            else:
                items.append(
                    MatchedItem(
                        favorite_id=fav.id,
                        query=fav.query,
                        quantity=fav.quantity,
                        product=None,
                        unit_price=None,
                    )
                )
        results.append(ChainTotal(chain=chain, items=items))

    return results
