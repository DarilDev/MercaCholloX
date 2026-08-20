"""Motor de "vale la pena el desvío" — funciones puras, sin red ni base de
datos, para que sean fáciles de testear y de auditar (un error de signo aquí
produciría veredictos incorrectos de forma silenciosa).

El llamador (app/api/worth_it.py) es responsable de conseguir los datos
reales (rutas de OSRM, precio de gasolina, totales de cesta) — este módulo
solo hace la aritmética, siguiendo el mismo principio de transparencia ya
aplicado en el matching de favoritos: cada término de la fórmula se expone,
nunca solo el veredicto final.
"""

from dataclasses import dataclass


@dataclass
class WorthItVerdict:
    detour_extra_km: float
    detour_extra_min: float
    fuel_cost_eur: float
    time_cost_eur: float
    basket_savings_eur: float
    net_savings_eur: float
    worth_it: bool


def detour_extra(
    home_to_candidate_km: float,
    home_to_candidate_min: float,
    candidate_to_work_km: float | None = None,
    candidate_to_work_min: float | None = None,
    home_to_work_km: float | None = None,
    home_to_work_min: float | None = None,
) -> tuple[float, float]:
    """Km/min de más que cuesta desviarse a la candidata, respecto a la ruta
    habitual. Con trabajo fijado: casa->candidata->trabajo menos casa->trabajo
    directo (si la tienda está de camino, esto puede salir ~0). Sin trabajo:
    viaje dedicado de ida y vuelta desde casa."""
    if (
        home_to_work_km is not None
        and home_to_work_min is not None
        and candidate_to_work_km is not None
        and candidate_to_work_min is not None
    ):
        extra_km = home_to_candidate_km + candidate_to_work_km - home_to_work_km
        extra_min = home_to_candidate_min + candidate_to_work_min - home_to_work_min
    else:
        extra_km = home_to_candidate_km * 2
        extra_min = home_to_candidate_min * 2
    # el ruido de OSRM (rutas ligeramente distintas por el mismo tramo) no
    # debería poder dar un desvío negativo
    return max(extra_km, 0.0), max(extra_min, 0.0)


def fuel_cost(extra_km: float, consumption_l_per_100km: float, fuel_price_eur_l: float) -> float:
    return round((extra_km / 100) * consumption_l_per_100km * fuel_price_eur_l, 2)


def time_cost(extra_min: float, hourly_value_eur: float) -> float:
    return round((extra_min / 60) * hourly_value_eur, 2)


def evaluate(
    *,
    basket_usual_eur: float,
    basket_candidate_eur: float,
    home_to_candidate_km: float,
    home_to_candidate_min: float,
    consumption_l_per_100km: float,
    fuel_price_eur_l: float,
    hourly_value_eur: float,
    candidate_to_work_km: float | None = None,
    candidate_to_work_min: float | None = None,
    home_to_work_km: float | None = None,
    home_to_work_min: float | None = None,
    threshold_eur: float = 0.5,
) -> WorthItVerdict:
    extra_km, extra_min = detour_extra(
        home_to_candidate_km,
        home_to_candidate_min,
        candidate_to_work_km,
        candidate_to_work_min,
        home_to_work_km,
        home_to_work_min,
    )
    f_cost = fuel_cost(extra_km, consumption_l_per_100km, fuel_price_eur_l)
    t_cost = time_cost(extra_min, hourly_value_eur)
    basket_savings = round(basket_usual_eur - basket_candidate_eur, 2)
    net_savings = round(basket_savings - f_cost - t_cost, 2)

    return WorthItVerdict(
        detour_extra_km=round(extra_km, 2),
        detour_extra_min=round(extra_min, 1),
        fuel_cost_eur=f_cost,
        time_cost_eur=t_cost,
        basket_savings_eur=basket_savings,
        net_savings_eur=net_savings,
        worth_it=net_savings > threshold_eur,
    )
