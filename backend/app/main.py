from fastapi import FastAPI

from app.api import favorites, products, profile, stores

# El esquema de la base de datos lo gestiona Alembic (`alembic upgrade head`),
# no un create_all() al arrancar — así no hay dos mecanismos de creación de
# tablas que puedan desincronizarse entre sí. Ver backend/README.md.
app = FastAPI(title="MercaChollo API")

app.include_router(products.router)
app.include_router(favorites.router)
app.include_router(profile.router)
app.include_router(stores.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    # Render comprueba por defecto si el servicio está listo pidiendo "/" —
    # sin esta ruta, Render marca la instancia como no lista y deja de
    # enrutarle tráfico aunque la app esté funcionando bien.
    return {"service": "mercachollo-api", "status": "ok"}
