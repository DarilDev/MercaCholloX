# MercaChollo — app móvil

App Android (Flutter) de MercaChollo. Cliente fino: la lógica real (precios, matching, comparación) vive en `../backend/`.

## Estructura

```
lib/
├── main.dart
├── models/       # Product, SupermarketCategory, Favorite, ShoppingComparison
├── services/      # api_client.dart — todas las llamadas al backend
├── screens/       # Pasillos, Buscar, Mi lista
└── widgets/       # ProductTile (imagen + precio + añadir a la lista)
```

## Arrancar en local (WSL2)

```bash
source ../scripts/env.sh   # carga Flutter/Android SDK/JDK (instalados sin apt, ver ../docs/DECISIONS.md)
flutter run                # con el móvil conectado por ADB inalámbrico
```

La URL del backend se configura en `lib/services/api_client.dart` — ver `../docs/DECISIONS.md` para cómo se expone (ngrok en desarrollo, migrando a Render — ver la sección "Arquitectura para escalar" del plan del proyecto).

## Tests

```bash
flutter test
```
