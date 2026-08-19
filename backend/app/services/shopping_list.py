"""Compara la lista de la compra (favoritos) entre las cadenas cacheadas.

Cada favorito es un texto genérico (ej. "leche entera"), no un producto de una
cadena concreta. Para cada cadena, se busca el producto más barato cuyo nombre
contenga todas las palabras del texto — el mismo matching por substring que ya
usa /products/search, así el resultado es explicable: se muestra qué producto
concreto se emparejó, no una caja negra.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Favorite, Product

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

    # current_price materializado por el worker de refresco — evita recalcular
    # MAX(id) sobre `prices` (que crece sin límite) en cada búsqueda.
    q = db.query(Product).filter(Product.chain == chain, Product.current_price.isnot(None))
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

    candidates.sort(key=lambda p: (noise(p), p.current_price))
    best = candidates[0]
    return best, best.current_price


def known_chains(db: Session) -> list[str]:
    return [row[0] for row in db.query(Product.chain).distinct().all()]


def compare_favorites(db: Session, user_id: int) -> list[ChainTotal]:
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
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
