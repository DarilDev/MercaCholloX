"""Utilidad de coincidencia de texto compartida entre el matching de
favoritos (shopping_list.py, "leche entera" -> producto real de cada cadena)
y el matching del escáner con nombres externos de OpenFoodFacts
(products.py) — mismo problema de fondo: encontrar el producto cacheado más
parecido a un texto libre, sin caja negra."""

_STOPWORDS = {
    "de", "del", "la", "el", "los", "las", "y", "en", "con", "sin", "para",
    "un", "una", "unos", "unas", "al", "a", "o",
}


def significant_words(text: str) -> list[str]:
    return [w for w in text.strip().lower().split() if w and w not in _STOPWORDS]
