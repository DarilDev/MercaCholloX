from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import CurrentUser
from app.models import FuelStation, Store, UserProfile
from app.schemas import WorthItOut
from app.services import osrm_client, overpass_client, scoring, shopping_list
from app.services.chain_aliases import normalize_chain_name
from app.services.geo import haversine_km

router = APIRouter(prefix="/worth-it", tags=["worth-it"])

# Candidata física: se busca en un radio mayor que el de /stores/nearby
# (que es solo para listar "lo que hay cerca") porque aquí hace falta
# encontrar UNA tienda real de la cadena, aunque no sea la más próxima posible.
_CANDIDATE_RADIUS_M = 5000

# Filtro grosero (caja ~1º ~ 111km) antes del haversine exacto — evita traer
# las ~11.000 gasolineras cacheadas en cada petición.
_FUEL_BOX_DEG = 0.5


def _nearest_fuel_price(db: Session, lat: float, lon: float, fuel_type: str) -> float | None:
    candidates = (
        db.query(FuelStation)
        .filter(FuelStation.lat.between(lat - _FUEL_BOX_DEG, lat + _FUEL_BOX_DEG))
        .filter(FuelStation.lon.between(lon - _FUEL_BOX_DEG, lon + _FUEL_BOX_DEG))
        .all()
    )
    priced = [s for s in candidates if getattr(s, fuel_type, None) is not None]
    if not priced:
        return None
    nearest = min(priced, key=lambda s: haversine_km(lat, lon, s.lat, s.lon))
    return getattr(nearest, fuel_type)


# Caja grosera antes del haversine exacto (mismo criterio que _nearest_fuel_price)
_CANDIDATE_BOX_DEG = 0.1  # ~11km


def _cached_candidate_store(db: Session, lat: float, lon: float, chain: str) -> tuple[float, float] | None:
    """Reutiliza tiendas ya cacheadas en `stores` (rellenada cada vez que
    alguien visita Ubicación/`/stores/nearby`) antes de llamar a Overpass en
    vivo — reduce cuánto dependemos de un servicio público con IP compartida
    en Render para el caso común (usuario que ya vio su zona una vez)."""
    candidates = (
        db.query(Store)
        .filter(Store.lat.isnot(None), Store.lon.isnot(None))
        .filter(Store.lat.between(lat - _CANDIDATE_BOX_DEG, lat + _CANDIDATE_BOX_DEG))
        .filter(Store.lon.between(lon - _CANDIDATE_BOX_DEG, lon + _CANDIDATE_BOX_DEG))
        .all()
    )
    matches = [s for s in candidates if normalize_chain_name(s.chain) == chain]
    if not matches:
        return None
    nearest = min(matches, key=lambda s: haversine_km(lat, lon, s.lat, s.lon))
    return nearest.lat, nearest.lon


def _nearest_candidate_store(db: Session, lat: float, lon: float, chain: str) -> tuple[float, float] | None:
    cached = _cached_candidate_store(db, lat, lon, chain)
    if cached is not None:
        return cached

    try:
        nearby = overpass_client.fetch_nearby_supermarkets(lat, lon, radius_m=_CANDIDATE_RADIUS_M)
    except overpass_client.OverpassClientError:
        return None
    matches = [s for s in nearby if normalize_chain_name(s.brand or s.name) == chain]
    if not matches:
        return None
    nearest = min(matches, key=lambda s: haversine_km(lat, lon, s.lat, s.lon))
    return nearest.lat, nearest.lon


@router.get("", response_model=list[WorthItOut])
def worth_it(user: CurrentUser, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile is None or profile.home_lat is None or profile.home_lon is None:
        raise HTTPException(status_code=400, detail="Fija tu casa en el perfil primero")

    chain_totals = {ct.chain: ct for ct in shopping_list.compare_favorites(db, user_id=user.id)}
    complete_chains = {c: ct for c, ct in chain_totals.items() if not ct.missing}
    if not complete_chains:
        raise HTTPException(status_code=400, detail="Sin datos de precio suficientes para comparar")

    usual_chain = None
    if profile.usual_store_id:
        usual_store = db.query(Store).filter(Store.id == profile.usual_store_id).first()
        if usual_store:
            usual_chain = normalize_chain_name(usual_store.chain) or usual_store.chain

    # Sin súper habitual fijado, o la cadena habitual no tiene datos de
    # precio propios (ej. es una cadena no trackeada): se usa la más barata
    # de las que sí tenemos como referencia, para no bloquear el cálculo.
    if usual_chain not in complete_chains:
        usual_chain = min(complete_chains, key=lambda c: complete_chains[c].total)

    usual_total = complete_chains[usual_chain].total

    fuel_price = _nearest_fuel_price(db, profile.home_lat, profile.home_lon, profile.fuel_type)
    if fuel_price is None:
        raise HTTPException(status_code=400, detail="Sin precio de combustible disponible cerca de casa")

    has_work = profile.work_lat is not None and profile.work_lon is not None

    results: list[WorthItOut] = []
    for chain, ct in complete_chains.items():
        if chain == usual_chain:
            continue

        candidate = _nearest_candidate_store(db, profile.home_lat, profile.home_lon, chain)
        if candidate is None:
            continue
        cand_lat, cand_lon = candidate

        try:
            home_to_candidate = osrm_client.route(profile.home_lat, profile.home_lon, cand_lat, cand_lon)
        except osrm_client.OsrmClientError:
            continue

        candidate_to_work = None
        home_to_work = None
        if has_work:
            try:
                candidate_to_work = osrm_client.route(cand_lat, cand_lon, profile.work_lat, profile.work_lon)
                home_to_work = osrm_client.route(
                    profile.home_lat, profile.home_lon, profile.work_lat, profile.work_lon
                )
            except osrm_client.OsrmClientError:
                candidate_to_work = None
                home_to_work = None

        verdict = scoring.evaluate(
            basket_usual_eur=usual_total,
            basket_candidate_eur=ct.total,
            home_to_candidate_km=home_to_candidate.distance_km,
            home_to_candidate_min=home_to_candidate.duration_min,
            consumption_l_per_100km=profile.vehicle_consumption_l_per_100km,
            fuel_price_eur_l=fuel_price,
            hourly_value_eur=profile.hourly_value_eur,
            candidate_to_work_km=candidate_to_work.distance_km if candidate_to_work else None,
            candidate_to_work_min=candidate_to_work.duration_min if candidate_to_work else None,
            home_to_work_km=home_to_work.distance_km if home_to_work else None,
            home_to_work_min=home_to_work.duration_min if home_to_work else None,
            threshold_eur=settings.worth_it_threshold_eur,
        )
        results.append(WorthItOut(chain=chain, usual_chain=usual_chain, **verdict.__dict__))

    results.sort(key=lambda r: r.net_savings_eur, reverse=True)
    return results
