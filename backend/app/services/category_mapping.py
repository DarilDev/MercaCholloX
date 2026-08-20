"""Mapeo manual de las categorías top-level ("pasillo") de cada cadena a una
taxonomía común. Cada cadena nombra sus pasillos a su manera (ej. "Charcutería
y quesos" en Mercadona vs "Quesos"/"Charcutería" por separado en Dia) — sin
este mapeo, navegar por pasillos mezclaría taxonomías distintas o, si se
separa por cadena, obligaría a elegir cadena antes de poder comparar nada,
que es justo lo contrario de para qué sirve la app.

Derivado a mano inspeccionando los `top_category` reales cacheados de cada
cadena (ver `SELECT DISTINCT chain, top_category` en la base de datos) — no
hay una fuente oficial que los relacione entre sí.

Al añadir una cadena nueva: mirar sus `top_category` reales y añadir su fila
aquí. Un `top_category` sin mapear no rompe nada — sus productos simplemente
no aparecen agrupados en ningún pasillo (quedan `canonical_category=None`,
solo visibles por búsqueda libre).
"""

CANONICAL_CATEGORIES: dict[str, dict[str, str]] = {
    "mercadona": {
        "Aceite, especias y salsas": "Aceite, especias y salsas",
        "Agua y refrescos": "Agua y refrescos",
        "Aperitivos": "Aperitivos y frutos secos",
        "Arroz, legumbres y pasta": "Arroz, legumbres y pasta",
        "Azúcar, caramelos y chocolate": "Azúcar, caramelos y chocolate",
        "Bebé": "Bebé / infantil",
        "Bodega": "Bodega",
        "Cacao, café e infusiones": "Cacao, café e infusiones",
        "Carne": "Carne",
        "Cereales y galletas": "Cereales y galletas",
        "Charcutería y quesos": "Charcutería y quesos",
        "Congelados": "Congelados",
        "Conservas, caldos y cremas": "Conservas, caldos y cremas",
        "Cuidado del cabello": "Cuidado del cabello",
        "Cuidado facial y corporal": "Cuidado facial y corporal",
        "Fitoterapia y parafarmacia": "Fitoterapia y parafarmacia",
        "Fruta y verdura": "Fruta y verdura",
        "Huevos, leche y mantequilla": "Huevos, leche y mantequilla",
        "Limpieza y hogar": "Limpieza y hogar",
        "Maquillaje": "Maquillaje",
        "Marisco y pescado": "Marisco y pescado",
        "Mascotas": "Mascotas",
        "Panadería y pastelería": "Panadería y pastelería",
        "Pizzas y platos preparados": "Pizzas y platos preparados",
        "Postres y yogures": "Postres y yogures",
        "Zumos": "Zumos",
    },
    "dia": {
        "Aceites, salsas y especias": "Aceite, especias y salsas",
        "Agua y refrescos": "Agua y refrescos",
        "Aperitivos y frutos secos": "Aperitivos y frutos secos",
        "Arroz, pastas y legumbres": "Arroz, legumbres y pasta",
        "Bollería, repostería y azúcar": "Panadería y pastelería",
        "Cabello y perfumería": "Cuidado del cabello",
        "Café, cacao e infusiones": "Cacao, café e infusiones",
        "Carnes": "Carne",
        "Cervezas, vinos y licores": "Bodega",
        "Charcutería": "Charcutería y quesos",
        "Charcutería y quesos": "Charcutería y quesos",
        "Chocolates y golosinas": "Azúcar, caramelos y chocolate",
        "Congelados y helados": "Congelados",
        "Conservas, caldos y cremas": "Conservas, caldos y cremas",
        "Frutas": "Fruta y verdura",
        "Galletas, cereales y mermeladas": "Cereales y galletas",
        "Higiene y cuidado del cuerpo": "Cuidado facial y corporal",
        "Huevos, leche y mantequilla": "Huevos, leche y mantequilla",
        "Infantil": "Bebé / infantil",
        "Limpieza y hogar": "Limpieza y hogar",
        "Mascotas": "Mascotas",
        "Panadería": "Panadería y pastelería",
        "Pescados y mariscos": "Marisco y pescado",
        "Platos preparados y pizzas": "Pizzas y platos preparados",
        "Quesos": "Charcutería y quesos",
        "Salud y parafarmacia": "Fitoterapia y parafarmacia",
        "Verduras": "Fruta y verdura",
        "Yogures y postres": "Postres y yogures",
        "Zumos y smoothies": "Zumos",
    },
}


def canonical_category(chain: str, raw_top_category: str | None) -> str | None:
    if raw_top_category is None:
        return None
    return CANONICAL_CATEGORIES.get(chain, {}).get(raw_top_category)
