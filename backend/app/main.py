from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import favorites, products
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="MercaChollo API", lifespan=lifespan)

app.include_router(products.router)
app.include_router(favorites.router)


@app.get("/health")
def health():
    return {"status": "ok"}
