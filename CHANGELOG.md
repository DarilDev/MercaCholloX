# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Este proyecto todavía no tiene versiones publicadas (beta privada) — las entradas se agrupan por fecha de sesión de trabajo, no por versión.

## [Sin publicar]

### Añadido — 2026-08-22 (continuación)
- **Fase 6: HiperDino integrado**, tercera cadena. Investigación en directo (agente `researcher`) confirmó que hiperdino.es (Magento) no tiene protección anti-bot: `POST /graphql` responde sin auth y sin rate-limit tras varias búsquedas seguidas. `hiperdino_client.py` sigue el mismo patrón que Dia (catálogo poblado por términos de búsqueda, no por árbol de categorías), pero cada producto trae su propia jerarquía de categorías reales — el pasillo sale gratis, a diferencia de Dia. Verificado extremo a extremo en local: 251 productos reales con nombre/precio/imagen/pasillo. Workflow de GitHub Actions manual (`refresh_hiperdino_prices.yml`), igual que se hizo con Dia hasta confirmar estabilidad. `chain_aliases.py` ampliado: el grupo Dinosol usa "HiperDino" y "SuperDino" para la misma cadena en OpenStreetMap.
- **Alcampo descartado** (ver docs/DATA_SOURCES.md): AWS WAF confirmado en directo — dejaba pasar 1 petición aislada pero bloqueaba con 403 a partir de la 2ª/3ª seguida, incluso con delays. No vale la pena sin infraestructura anti-detección seria.

### Añadido — 2026-08-22
- **Historial de precios**: la tabla `prices` (append-only desde el diseño inicial) se usa por fin de verdad — ficha de producto nueva con gráfico (`fl_chart`) y una etiqueta que distingue una bajada real de "el mismo precio de siempre" (compara contra la media de 30 días). Verificado en el móvil real con datos reales.
- **Escáner de código de barras** estilo Yuka: Nutri-Score, nivel de procesado NOVA y aditivos vía OpenFoodFacts (`GET /products/scan/{ean}`), con el precio real de la caché si el producto coincide. Pestaña "Escanear" nueva, empujada como ruta aparte del `IndexedStack` para no mantener la cámara encendida de fondo en el resto de pestañas.
- **Historial de escaneos**: los últimos 50 escaneos con éxito quedan guardados por dispositivo, para añadirlos a la lista más tarde sin volver a escanear. Botón "Añadir a mi lista" tanto en el resultado de un escaneo como en el historial.
- Bug real reportado por Daril probando en directo: el escáner "confundía" productos de cadenas sin integrar (ej. Lidl) con precios de Mercadona que no tenían nada que ver — el matching anclaba en la primera palabra del nombre y enganchaba cualquier producto que la compartiera. Corregido exigiendo todas las palabras significativas (extraído a `text_matching.py`, compartido con el matching de favoritos) — sin coincidencia es preferible a una coincidencia falsa.
- **App más ligera**: `minifyEnabled`/`shrinkResources` y build partido por ABI, que no estaban activados — el APK universal no encogía código ni recursos. El APK que de verdad se instala en un móvil real (arm64) pasó de 54.0MB a 25.8MB, medido antes/después.
- Investigado (sin construir): próxima cadena tras Dia — ver "En curso" arriba. Confirmado también que Lidl tiene presencia real en OpenFoodFacts a nivel global (no solo las cadenas ya integradas).

### Añadido — 2026-08-21
- **Fiabilidad real en producción**: Overpass y OSRM fallaban de forma intermitente en Render porque el plan gratuito reparte una IP de salida compartida entre todos sus clientes — si otro proyecto agotaba la cuota de una API pública, la IP compartida quedaba limitada para todos. Arreglado con una lista de mirrors de respaldo por servicio (un intento por URL, no reintentar la misma contra un 429).
- **Causa real del cuelgue de `/stores/nearby` y `/worth-it`**: escribían las tiendas encontradas una a una contra Neon en vez de en lote. Con `UNIQUE(chain, external_id)` + upsert por lotes, 453 tiendas pasaron de tardar más de 90s a 9.5s (y a ~1s sirviendo desde caché local).
- Permiso `INTERNET` que faltaba en `AndroidManifest.xml` — causaba "Failed host lookup" en toda petición de red del móvil.
- **Navegación cadena primero**, revirtiendo el intento de pasillo unificado del día anterior — decisión explícita de Daril: en Canarias no hay Dia, así que Aldi/Lidl/Carrefour/Alcampo deben priorizarse, y prefiere navegar cadena → dentro, productos, no una lista mezclada.
- Campo de dirección escribible (`AddressSearchField`, Photon con Nominatim de respaldo) en Ubicación — antes solo se podía fijar casa/trabajo por GPS.
- Tema compartido (`theme.dart`, `LoadingView`, `ErrorView`) sustituyendo ~7 implementaciones sueltas de carga/error.
- `/products/search` ordenaba alfabéticamente y enterraba productos reales bajo coincidencias parciales (ej. cosméticos antes que aceite de oliva de verdad) — ahora ordena por relevancia (menos palabras de más), mismo criterio que el matching de favoritos.
- Buscador y sugerencias de "Mi lista" en vivo (con debounce y foto real del producto) en vez de exigir el término exacto sin pistas visuales.
- Ubicación se quedaba cargando para siempre si fallaba la carga de súper cercanos — sin manejo de errores.

### Añadido — 2026-08-20
- **Fase 5: motor "vale la pena el desvío"** — compara la cadena habitual contra otra con mejor precio en la cesta, restando el coste de gasolina (MITECO) y de tiempo del desvío (OSRM); tarjeta de veredicto en la app con desglose expandible.
- Pasillos separados por cadena (antes mezclaba taxonomías de Mercadona y Dia) y mapa real (`flutter_map`) en Ubicación con casa/trabajo/súper cercanos.
- Mostrar el error real en vez de quedarse en "vacío" o colgado cuando falla la carga de cadenas o de la lista de favoritos.

### Añadido — 2026-08-19 (madrugada)
- Navegación por pasillos separada por cadena: `/categories` y `/products` ahora requieren `chain`, más un endpoint `GET /chains`. Antes mezclaba la taxonomía de Mercadona y Dia en la misma lista de "Pasillos" (49 entradas sin sentido) — ahora hay un selector arriba de la pantalla.
- Mapa real (`flutter_map` + OpenStreetMap) en la pantalla de Ubicación: casa, trabajo y súper cercanos como marcadores, además de la lista de siempre.
- La búsqueda (que sí mezcla cadenas a propósito) ahora muestra de qué cadena es cada resultado.

### Añadido — 2026-08-19 (noche)
- **Render y Neon en producción real**: backend desplegado en `https://mercachollo-api.onrender.com` (`render.yaml`), base de datos en Neon con el catálogo completo cargado. Arreglado un bug real de Render: comprueba por defecto si el servicio está listo pidiendo `/`, que no existía — la app se marcaba como no lista y Render le cortaba el tráfico pese a estar funcionando. La app ya no depende de ngrok.
- **Fase 2 y 3 cerradas con UI real**: pantalla "Ubicación" en la app — casa/trabajo con GPS real (`geolocator`), lista de súper físicos reales cerca (OpenStreetMap Overpass, con distancia), marcar el habitual. `overpass_client.py` tuvo que resolver un 406 real: Overpass rechaza peticiones cuyo User-Agent imita un navegador.
- **Fase 4: Dia integrado**, segunda cadena con variación de precio real. Selenium (con y sin `undetected-chromedriver`) recibe "Access Denied" de Akamai en dia.es, pero peticiones HTTP simples sí pasan — no hacía falta Selenium después de todo. Endpoint real descubierto a mano (`/api/v1/search-back/search`), catálogo poblado buscando ~40 términos habituales (sin árbol de categorías navegable encontrado). Checkpoint del plan confirmado: aceite de oliva a 3,80€ en Mercadona vs 3,99€ en Dia, mismo producto real en ambos.
- Workflows de GitHub Actions aislados por cadena — Mercadona programado a diario, Dia solo manual por ahora (Akamai de por medio, mejor confirmar que aguanta antes de dejarlo desatendido).

### Añadido — 2026-08-19 (tarde)
- Identidad por dispositivo (`X-Device-Id`): tabla `users`, favoritos y perfil ya no son globales — cada dispositivo ve solo su propia lista. Verificado con dos identidades distintas.
- Alembic: el esquema deja de gestionarse con `create_all()`, primera migración generada y aplicada.
- `Product.current_price` materializado por el worker de refresco — las búsquedas y la comparación de lista dejan de recalcular `MAX(id)` sobre `prices` en cada petición (el coste se habría duplicado al añadir Dia).
- Unicidad `(chain, external_id)` en `Product` — evita duplicados cuando exista un segundo worker de refresco (Dia).
- `config.py` listo para Postgres: `MERCACHOLLO_DATABASE_URL` (con normalización automática del driver, `postgres://` → `postgresql+psycopg://`), corregido de paso un bug real — el prefijo `MERCACHOLLO_` que `.env.example` ya documentaba nunca estaba configurado en `Settings`, así que ninguna variable de entorno personalizada surtía efecto.
- Flutter: URL del backend configurable en tiempo de ejecución (`shared_preferences` + pantalla de Ajustes), en vez de hardcodeada — ya no hace falta recompilar para repartir una nueva URL a los testers.
- Workflow de GitHub Actions para el refresco programado de Mercadona, listo pero con disparo manual (`workflow_dispatch`) hasta que exista el secret de conexión a Neon.
- README raíz y CHANGELOG creados; README de `mobile/` (boilerplate de `flutter create` sin rellenar) sustituido por contenido real.

### Añadido — 2026-08-19
- Arquitectura para escalar revisada explícitamente (ver `docs/DECISIONS.md`): distinción entre bugs a arreglar ya, mejoras baratas-ahora-caras-después, e infraestructura deliberadamente diferida con su disparador concreto.
- SQLite en modo WAL + `busy_timeout` — evita bloqueos si el refresco corre a la vez que alguien usa la app.
- Cliente de Mercadona con reintento acotado, backoff/jitter, y una excepción específica (`MercadonaBlockedError`) que aborta el refresco entero ante un 429/403 en vez de insistir.
- Test que golpea la API real de Mercadona aislado con `@pytest.mark.live`, excluido por defecto.
- Navegación por pasillos tipo supermercado (categorías → subcategorías → productos) con imágenes reales de Mercadona.
- Pantalla "Mi lista de la compra": favoritos como texto genérico (ej. "leche entera"), comparados automáticamente entre las cadenas cacheadas.
- Corregido el matching de favoritos: priorizar el nombre de producto más cercano a la búsqueda (menos palabras de más), precio solo como desempate — el enfoque anterior ("más barato que contenga las palabras") emparejaba mal (ej. un tarrito de tomate con "aceite de oliva" en el nombre ganaba a una botella real de aceite).
- Investigación de apps similares (Chollometro, Yuka, Too Good To Go) para fundamentar mejoras futuras — ver sección correspondiente del plan.
- Repositorio conectado y sincronizado con `github.com/DarilDev/MercaCholloX`.

### Añadido — 2026-08-18
- Backend (FastAPI + SQLite): pipeline real de precios de Mercadona (API pública no oficial, verificada a mano), caché local de productos y precios (`prices` append-only, pensado desde el principio para histórico), endpoint de búsqueda.
- App Flutter (Android): pantalla de búsqueda conectada al backend real.
- Toolchain de desarrollo (JDK, Android SDK, Flutter, ngrok) instalado de forma portable en WSL2, sin `apt`/sudo (no disponible en esta máquina).
- App instalada y probada en dispositivo Android real vía ADB inalámbrico, backend expuesto por túnel ngrok.
- Investigación y descarte de Lidl y Carrefour como próxima cadena (verificado en directo: Lidl no vende alimentación online en España; Carrefour bloquea peticiones simples). Dia elegido como próxima cadena.
