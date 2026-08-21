"""Endpoint de diagnóstico temporal — investigar por qué Overpass falla
desde Render (todas las URLs configuradas fallaron, 49.7s, sin datos).
Prueba cada URL configurada de Overpass/OSRM directamente y devuelve el
error real de cada una, en vez de solo "vacío" como ven los endpoints
normales. Se borra en cuanto se identifique la causa."""

import httpx
from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/debug", tags=["debug"])


_REAL_QUERY = (
    "[out:json][timeout:20];"
    '(node["shop"="supermarket"](around:5000,40.4168,-3.7038);'
    'way["shop"="supermarket"](around:5000,40.4168,-3.7038););'
    "out center;"
)


@router.get("/overpass-check")
def overpass_check():
    """Usa la MISMA query que overpass_client.py de verdad (way+node,
    out center, 5000m) — la primera versión de este endpoint usaba una query
    más simple y daba resultados distintos a los del endpoint real."""
    results = []
    for url in settings.overpass_urls:
        entry = {"url": url}
        import time as _time

        started = _time.monotonic()
        try:
            resp = httpx.post(
                url,
                data={"data": _REAL_QUERY},
                headers={
                    "User-Agent": "MercaChollo/1.0 (proyecto personal, sin fines comerciales)",
                    "Accept": "*/*",
                    "Accept-Encoding": "identity",
                },
                timeout=25.0,
            )
            entry["status_code"] = resp.status_code
            entry["elements"] = len(resp.json().get("elements", [])) if resp.status_code == 200 else None
        except Exception as exc:
            entry["error_type"] = type(exc).__name__
            entry["error"] = str(exc)
        entry["seconds"] = round(_time.monotonic() - started, 2)
        results.append(entry)
    return {"overpass_urls": results}


@router.get("/osrm-check")
def osrm_check():
    results = []
    for base_url in settings.osrm_urls:
        entry = {"url": base_url}
        try:
            resp = httpx.get(
                f"{base_url}/route/v1/driving/-3.7038,40.4168;-3.7065,40.4146",
                params={"overview": "false"},
                timeout=12.0,
            )
            entry["status_code"] = resp.status_code
            entry["body_preview"] = resp.text[:200]
        except Exception as exc:
            entry["error_type"] = type(exc).__name__
            entry["error"] = str(exc)
        results.append(entry)
    return {"osrm_urls": results}
