# Fuentes de datos — MercaChollo

## Cadenas de supermercado

| Cadena | Estado | Acceso |
|---|---|---|
| **Mercadona** | ✅ Confirmado y en uso (Fase 1) | API JSON pública sin autenticación, verificada a mano: `GET https://tienda.mercadona.es/api/categories/?lang=es&wh={wh}` (árbol de categorías) y `GET /api/categories/{id}/?lang=es&wh={wh}` (subcategorías + productos + `price_instructions.unit_price`). Documentada por la comunidad: github.com/datania/mercadona-catalog, github.com/javichur/merca-api. Precios prácticamente uniformes en toda España (ver DECISIONS.md). |
| **Dia** | ✅ Confirmado y en uso (Fase 4) | **Verificado en directo, con matices**: dia.es está detrás de Akamai — Selenium (con y sin `undetected-chromedriver`) recibe "Access Denied" cargando la home, coincide con lo que sugería el scraper de referencia (github.com/vgvr0/dia-supermarket-scraper, que por eso usa Selenium). **Pero peticiones HTTP simples (sin ejecutar JS) SÍ pasan** — no hace falta Selenium/Chrome al final. Endpoint real descubierto inspeccionando el JSON embebido en la página de búsqueda (`vike_pageContext.endpoints.search.client`): `GET https://www.dia.es/api/v1/search-back/search?q={término}`, con cabeceras `cart_id`/`session_id`/`customer_id`/`x-locale` — verificado que aceptan valores generados por nosotros (UUIDs propios), no hace falta sesión previa. Sin árbol de categorías navegable encontrado — el catálogo se puebla buscando ~40 términos habituales de la compra (`dia_client.SEARCH_TERMS`); cada resultado ya trae su categoría real de Dia. Variación de precio real confirmada frente a Mercadona (ej. aceite de oliva: 3,80€ Hacendado vs 3,99€ Carbonell). |
| **Carrefour** | ❌ Descartado por ahora | **Verificado en directo**: carrefour.es devuelve `403 Forbidden` a una petición simple con user-agent de navegador — protección anti-bot más agresiva que Dia. No se persigue salvo que aparezca una razón de peso para invertir en sortear esa protección. |
| **Lidl** | ❌ Descartado (no aplica) | **Verificado en directo/por búsqueda**: lidl.es **no vende alimentación online** en España, solo artículos no alimentarios. La compra de comida real (con precios de tienda física) se hace a través de un socio externo, **Lola Market**, y solo en Madrid/Barcelona/Valencia — sin API pública confirmada. No hay camino gratuito y fiable para sacar precios de productos básicos (ej. leche) de Lidl ahora mismo. |
| **Aldi** | 🔜 No evaluado en profundidad | Aldi US tiene un scraper que usa una API interna (github.com/stiles/aldi), sugiere que aldi.es podría ser similar, pero no verificado en directo para España. Baja prioridad mientras Dia cubre la necesidad de una 2ª cadena. |
| **Consum / Alcampo / Eroski** | 🔜 No evaluado en profundidad | Consum devuelve 200 pero es una SPA sin pistas de API en el HTML estático (necesitaría inspección con navegador real, no solo `curl`). Alcampo redirige (301, sin explorar destino). Eroski no respondió. No se ha invertido más tiempo aquí — Dia ya cubre la necesidad inmediata. |

## Otras fuentes

- **Ubicación de tiendas físicas**: OpenStreetMap Overpass API — `https://overpass-api.de/api/interpreter`, gratis, sin key, nodos `shop=supermarket` con tag `brand`.
- **Distancia/tiempo de conducción real**: OSRM (Open Source Routing Machine) — demo público `https://router.project-osrm.org` o autoalojado.
- **Precio real de combustible**: Geoportal de Hidrocarburos del MITECO (sistema SIPP), datos abiertos también en datos.gob.es — gasolineras obligadas por ley a reportar cambios en 24h.

## Nota sobre legalidad/buenas prácticas

Estas APIs son endpoints públicos no autenticados usados por las propias webs de los supermercados para mostrar sus catálogos — leer datos públicos de esta forma es una práctica técnica común y documentada por la comunidad (ver repos citados arriba). Aun así, para ser buenos vecinos de estos servicios: identificar el cliente con un `User-Agent` propio (ya hecho en `mercadona_client.py`), cachear en vez de repetir peticiones innecesarias, y no hacer scraping agresivo/paralelo masivo. No es asesoría legal — si la app pasa de beta privada a algo más público, revisar términos de servicio de cada cadena en ese momento.
