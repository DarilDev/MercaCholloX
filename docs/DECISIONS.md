# Decisiones de diseño — MercaChollo

## Por qué Mercadona primero, aunque el objetivo final sea multi-cadena

Verificado por búsqueda web: Mercadona mantiene precios prácticamente idénticos en toda España (29 de 30 productos comparados, iguales en Madrid/Sevilla/Valencia/Bilbao; solo una excepción puntual en Barcelona). Esto significa que **el motor de "vale la pena desviarse" no tiene nada que optimizar si solo existe Mercadona** — dos tiendas Mercadona siempre van a costar lo mismo.

Por eso el roadmap separa dos cosas que parecían la misma tarea:
1. Montar el pipeline técnico (API real → caché → modelo de datos → app) — Mercadona es la mejor cadena para esto porque su API es la más limpia y ya está verificada.
2. Que el algoritmo de scoring tenga variación de precio real que explotar — eso requiere una segunda cadena con precios distintos por tienda/ciudad (Dia, Fase 4).

## Cadenas objetivo (actualizado)

Además de Mercadona (Fase 1) y Dia (Fase 4), Daril pidió añadir **Lidl** y **Aldi**. Ninguna de las dos tiene una API pública de catálogo tan limpia como la de Mercadona (ver docs/DATA_SOURCES.md) — se tratan como Fase 4b: se evalúan y se integran cuando el pipeline multi-cadena ya funcione con Dia, no antes, para no bloquear el progreso con la cadena más incierta primero.

## Por qué el `wh` (almacén) de Mercadona no es el mecanismo de "tienda física"

La API de Mercadona organiza los precios/disponibilidad por almacén de reparto (código postal), no por tienda física individual — encaja con que sea una tienda *online*. Para "encuentra el súper físico más cercano" el dato real de ubicación viene de OpenStreetMap Overpass (Fase 3), no de la API de Mercadona.
