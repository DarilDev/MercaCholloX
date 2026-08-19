from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Favorite
from app.schemas import (
    ChainTotalOut,
    FavoriteIn,
    FavoriteOut,
    MatchedItemOut,
    ProductOut,
    ShoppingComparisonOut,
)
from app.services import shopping_list

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteOut])
def list_favorites(db: Session = Depends(get_db)):
    return db.query(Favorite).all()


@router.post("", response_model=FavoriteOut)
def add_favorite(payload: FavoriteIn, db: Session = Depends(get_db)):
    favorite = Favorite(query=payload.query.strip(), quantity=payload.quantity)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
    if favorite is None:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    db.delete(favorite)
    db.commit()
    return {"deleted": favorite_id}


@router.get("/compare", response_model=ShoppingComparisonOut)
def compare_favorites(db: Session = Depends(get_db)):
    """Para cada cadena con datos cacheados, calcula el total de la lista de
    favoritos (emparejando el producto más barato que encaje en cada uno) y
    señala cuál sale más barata en conjunto."""
    chain_totals = shopping_list.compare_favorites(db)

    chains_out = []
    for ct in chain_totals:
        items_out = [
            MatchedItemOut(
                favorite_id=item.favorite_id,
                query=item.query,
                quantity=item.quantity,
                matched_product=(
                    ProductOut(
                        id=item.product.id,
                        chain=item.product.chain,
                        external_id=item.product.external_id,
                        name=item.product.name,
                        top_category=item.product.top_category,
                        category=item.product.category,
                        unit=item.product.unit,
                        image_url=item.product.image_url,
                        price=item.unit_price,
                    )
                    if item.product
                    else None
                ),
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in ct.items
        ]
        chains_out.append(
            ChainTotalOut(chain=ct.chain, items=items_out, total=ct.total, missing=ct.missing)
        )

    # solo se declara "más barata" una cadena que tenga todos los artículos —
    # si le faltan productos no es una comparación justa.
    complete_chains = [c for c in chains_out if not c.missing]
    cheapest = min(complete_chains, key=lambda c: c.total).chain if complete_chains else None

    return ShoppingComparisonOut(chains=chains_out, cheapest_chain=cheapest)
