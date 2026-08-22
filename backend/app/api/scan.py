from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.products import _best_match, _to_product_out
from app.db import get_db
from app.deps import CurrentUser
from app.models import ScanHistoryEntry
from app.schemas import ScanHistoryEntryOut, ScanResultOut
from app.services import openfoodfacts_client as off

router = APIRouter(tags=["scan"])


# Registrado antes de /products/scan/{ean}: si fuera al revés, "history"
# matchearía como si fuera un EAN (Starlette prueba las rutas en orden).
@router.get("/products/scan/history", response_model=list[ScanHistoryEntryOut])
def scan_history(user: CurrentUser, db: Session = Depends(get_db)):
    """Últimos escaneos de este dispositivo, para poder añadirlos a la lista
    más tarde sin tener que volver a escanear."""
    entries = (
        db.query(ScanHistoryEntry)
        .filter(ScanHistoryEntry.user_id == user.id)
        .order_by(ScanHistoryEntry.scanned_at.desc())
        .limit(50)
        .all()
    )
    return [
        ScanHistoryEntryOut(
            id=e.id,
            ean=e.ean,
            name=e.name,
            image_url=e.image_url,
            nutriscore_grade=e.nutriscore_grade,
            scanned_at=e.scanned_at.isoformat(),
        )
        for e in entries
    ]


@router.get("/products/scan/{ean}", response_model=ScanResultOut)
def scan_barcode(ean: str, user: CurrentUser, db: Session = Depends(get_db)):
    """Escanear un código de barras: consulta OpenFoodFacts (Nutri-Score,
    nivel de procesado NOVA, aditivos) y, si el nombre encaja con algo ya
    cacheado, añade el precio real — mismo principio de transparencia que el
    resto de la app, nunca solo un semáforo. Cada escaneo con éxito queda en
    el historial (solo lo encontrado en OpenFoodFacts, no los fallos)."""
    try:
        product = off.get_product(ean)
    except off.OpenFoodFactsError as exc:
        raise HTTPException(status_code=502, detail="No se pudo consultar OpenFoodFacts") from exc

    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado en OpenFoodFacts")

    db.add(
        ScanHistoryEntry(
            user_id=user.id,
            ean=product.ean,
            name=product.name,
            image_url=product.image_url,
            nutriscore_grade=product.nutriscore_grade,
        )
    )
    db.commit()

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
