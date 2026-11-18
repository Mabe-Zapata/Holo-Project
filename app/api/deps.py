"""Dependencias compartidas por las rutas."""

from functools import lru_cache

from fastapi import Depends, Header, HTTPException, Request, status


from app.core.config import obtener_configuracion
from app.services.almacen import CUENTAS_DEMO
from app.services.prompts import cargar_prompt_sistema
from app.services.proveedor_llm import ProveedorDiferido, ProveedorLLM, crear_proveedor
from app.services.riesgo import cargar_expresiones

def obtener_conexion(request: Request):
    motor = request.app.state.motor

    with motor.begin() as conexion:
        yield conexion

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


# Solo estas cuentas conversan con el asistente. El tratante recibe resúmenes (odds/chat.md).
ROLES_CONVERSACION = {"usuario_estandar", "paciente"}


def exigir_conversacion(usuario: dict = Depends(obtener_usuario)) -> dict:
    if usuario["rol"] not in ROLES_CONVERSACION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta no conversa con el asistente.",
        )
    return usuario


@lru_cache
def obtener_expresiones() -> tuple[str, ...]:
    return tuple(cargar_expresiones(obtener_configuracion().ruta_expresiones_riesgo))


@lru_cache
def obtener_proveedor() -> ProveedorLLM:
    cfg = obtener_configuracion()
    return ProveedorDiferido(
        lambda: crear_proveedor(
            cfg.proveedor_llm,
            clave=cfg.llm_api_key,
            modelo=cfg.llm_modelo,
            url_base=cfg.llm_url_base,
            prompt=cargar_prompt_sistema().texto,
        )
    )
