from fastapi import APIRouter

from app.core.config import obtener_configuracion

router = APIRouter(tags=["salud"])


@router.get("/salud", summary="Comprueba que la API está en funcionamiento")
def salud() -> dict:
    cfg = obtener_configuracion()
    return {"estado": "ok", "version": cfg.version}
