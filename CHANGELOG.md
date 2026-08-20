# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Este proyecto todavía no tiene versiones publicadas (beta privada) — las entradas se agrupan por fecha de sesión de trabajo, no por versión.

## [Sin publicar]

### En curso
- Fase 5: motor de scoring "vale la pena el desvío" (MITECO + OSRM + fórmula de ahorro neto).

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
