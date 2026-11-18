"""Dependencias compartidas por las rutas."""

from functools import lru_cache

from fastapi import Header, HTTPException, status

from app.core.config import obtener_configuracion
from app.services.almacen import CUENTAS_DEMO
from app.services.prompts import cargar_prompt_sistema
from app.services.proveedor_llm import ProveedorLLM, crear_proveedor
from app.services.riesgo import cargar_expresiones


def obtener_usuario(
    x_usuario_id: str = Header(
        ...,
        description="Identificador de la cuenta de demostración: ana, luis o tratante.",
    ),
) -> dict:
    cuenta = CUENTAS_DEMO.get(x_usuario_id)
    if cuenta is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta de demostración desconocida.",
        )
    return {"id": x_usuario_id, **cuenta}


@lru_cache
def obtener_expresiones() -> tuple[str, ...]:
    return tuple(cargar_expresiones(obtener_configuracion().ruta_expresiones_riesgo))


@lru_cache
def obtener_proveedor() -> ProveedorLLM:
    cfg = obtener_configuracion()
    return crear_proveedor(
        cfg.proveedor_llm,
        clave=cfg.llm_api_key,
        modelo=cfg.llm_modelo,
        url_base=cfg.llm_url_base,
        prompt=cargar_prompt_sistema().texto,
    )
