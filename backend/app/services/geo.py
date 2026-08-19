"""Distancia en línea recta — rápida, sin llamada externa. Para distancia/
tiempo de conducción real usar services/osrm_client.py (más caro, se reserva
para cuando ya se sabe qué candidato concreto se quiere evaluar, no para
listar decenas de tiendas cercanas)."""

from math import asin, cos, radians, sin, sqrt

_EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return round(2 * _EARTH_RADIUS_KM * asin(sqrt(a)), 2)
