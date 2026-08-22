"""OpenStreetMap tiene varios nombres/brand distintos para la misma cadena
real (verificado en directo cerca de Madrid: "Dia", "Dia Market", "Maxi Dia",
"La Plaza de DIA", "Supermercados Dia" son todo Dia) — hace falta normalizar
antes de comparar contra `Product.chain` ("mercadona", "dia"), o nunca se
encontraría la tienda física candidata de una cadena con datos de precio.

Al añadir una cadena nueva a `category_mapping.py`, revisar también aquí qué
variantes usa OSM para su nombre real (mismo tipo de trabajo manual).

**HiperDino** (verificado en directo cerca de Las Palmas de Gran Canaria):
el mismo grupo (Dinosol) opera dos formatos de tienda física, "HiperDino" y
"SuperDino" — mismo catálogo/precios online en hiperdino.es, así que ambos
mapean a la cadena "hiperdino".
"""

_ALIASES: dict[str, str] = {
    "mercadona": "mercadona",
    "dia": "dia",
    "dia market": "dia",
    "maxi dia": "dia",
    "la plaza de dia": "dia",
    "supermercados dia": "dia",
    "hiperdino": "hiperdino",
    "superdino": "hiperdino",
    "aldi": "aldi",
}


def normalize_chain_name(osm_name: str) -> str | None:
    return _ALIASES.get(osm_name.strip().lower())
