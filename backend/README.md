# MercaChollo backend

## Arrancar en local

```bash
cd backend
python3 -m venv venv          # si falla por "ensurepip is not available":
                               #   python3 -m pip install --user virtualenv
                               #   python3 -m virtualenv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/alembic upgrade head    # crea/actualiza el esquema — obligatorio antes del primer arranque
./venv/bin/uvicorn app.main:app --reload
```

- Swagger UI (probar endpoints desde el navegador, sin curl): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- La mayoría de endpoints necesitan el header `X-Device-Id` (cualquier string único vale para probar a mano, ej. `curl -H "X-Device-Id: prueba-manual" ...`) — ver `app/deps.py`.

## Migraciones (Alembic)

El esquema lo gestiona Alembic, no un `create_all()` automático — así una base de datos con datos reales nunca se queda con columnas a medio crear.

```bash
./venv/bin/alembic upgrade head                          # aplicar migraciones pendientes
./venv/bin/alembic revision --autogenerate -m "mensaje"   # generar una nueva tras cambiar app/models.py
```

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
