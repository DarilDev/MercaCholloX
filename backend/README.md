# MercaChollo backend

## Arrancar en local

```bash
cd backend
python3 -m venv venv          # si falla por "ensurepip is not available":
                               #   python3 -m pip install --user virtualenv
                               #   python3 -m virtualenv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn app.main:app --reload
```

- Swagger UI (probar endpoints desde el navegador, sin curl): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Rellenar la caché de precios (Mercadona)

```bash
./venv/bin/python -m app.workers.refresh_prices --limit 10   # prueba rápida
./venv/bin/python -m app.workers.refresh_prices              # catálogo completo (~100+ categorías)
```

## Tests

```bash
./venv/bin/python -m pytest tests/ -q
```

Ver `docs/DATA_SOURCES.md` y `docs/DECISIONS.md` (en la raíz del proyecto) para el porqué de cada fuente de datos y decisión de arquitectura.
