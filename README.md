# MercaChollo

App Android (Flutter) + backend (Python/FastAPI) que compara precios reales de supermercados y ayuda a decidir si merece la pena desviarse a otro súper más barato, teniendo en cuenta la ubicación, el coste de gasolina del desvío y el coste de oportunidad del tiempo — no solo el precio del producto.

## Por qué existe

Apps como Soysuper, OCU o FindItApp comparan cestas de compra para pedir *online* a domicilio. Ninguna cruza el precio con la cercanía física real ni con el coste de desplazarse — ese es el hueco que cubre MercaChollo. Más contexto y decisiones de producto en [docs/DECISIONS.md](docs/DECISIONS.md).

## Estado actual

Beta privada en desarrollo (familia/amigos, sin publicar en Play Store). Ver [CHANGELOG.md](CHANGELOG.md) para el detalle de qué hay construido y [docs/DECISIONS.md](docs/DECISIONS.md) para el porqué de cada decisión de arquitectura.

- **Backend**: pipeline real de precios de Mercadona, Dia e HiperDino (categorías, productos, imágenes), navegación tipo supermercado por pasillos, búsqueda, lista de la compra que compara el total entre cadenas, motor "vale la pena el desvío" (gasolina real + coste de tiempo), historial de precios y escáner de código de barras (Nutri-Score/NOVA).
- **App**: Android nativo (Flutter), instalada y probada en dispositivo real vía ADB inalámbrico.
- **Próxima cadena**: sin decidir — Alcampo descartado (AWS WAF), Aldi/Consum/Eroski sin evaluar en profundidad (ver [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)).

## Estructura

```
backend/   API en Python (FastAPI) — toda la lógica de negocio vive aquí
mobile/    App Flutter (Android) — cliente fino, poca lógica propia
docs/      Decisiones de arquitectura y fuentes de datos, con su porqué
scripts/   Utilidades de desarrollo (entorno WSL2, arranque del backend)
```

## Arrancar en local

Backend: ver [backend/README.md](backend/README.md).

Móvil (WSL2): `source scripts/env.sh` para cargar el toolchain (Flutter/Android SDK/JDK instalados sin `apt`, ver [docs/DECISIONS.md](docs/DECISIONS.md)), luego `cd mobile && flutter run`.
