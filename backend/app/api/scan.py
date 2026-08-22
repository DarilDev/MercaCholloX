from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.products import _best_match, _to_product_out
from app.db import get_db
from app.schemas import ScanResultOut
from app.services import openfoodfacts_client as off

router = APIRouter(tags=["scan"])


@router.get("/products/scan/{ean}", response_model=ScanResultOut)
def scan_barcode(ean: str, db: Session = Depends(get_db)):
    """Escanear un código de barras: consulta OpenFoodFacts (Nutri-Score,
    nivel de procesado NOVA, aditivos) y, si el nombre encaja con algo ya
    cacheado, añade el precio real — mismo principio de transparencia que el
    resto de la app, nunca solo un semáforo."""
    try:
        product = off.get_product(ean)
    except off.OpenFoodFactsError as exc:
        raise HTTPException(status_code=502, detail="No se pudo consultar OpenFoodFacts") from exc

    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado en OpenFoodFacts")

    matched = _best_match(db, product.name) if product.name else None
    return ScanResultOut(
        ean=product.ean,
        name=product.name,
        image_url=product.image_url,
        nutriscore_grade=product.nutriscore_grade,
        nova_group=product.nova_group,
        additives_count=product.additives_count,
        matched_product=_to_product_out(matched) if matched else None,
    )
