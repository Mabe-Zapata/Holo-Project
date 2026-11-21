"""Dependencias compartidas por las rutas."""

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.engine import Connection, Engine

from app.core.config import obtener_configuracion
from app.db import crear_motor, crear_tablas
from app.repositorios.usuarios import crear_cuentas_demo
from app.services.almacen import CUENTAS_DEMO
from app.services.cola import ColaPendientes
from app.services.prompts import cargar_prompt_sistema
from app.services.proveedor_llm import ProveedorDiferido, ProveedorLLM, crear_proveedor
from app.services.resumen import crear_resumidor
from app.services.riesgo import cargar_expresiones

_motor_defecto: Engine | None = None


def _obtener_motor_por_defecto() -> Engine:
    global _motor_defecto
    if _motor_defecto is None:
        _motor_defecto = crear_motor("sqlite:///:memory:")
        crear_tablas(_motor_defecto)
        with _motor_defecto.begin() as conexion:
            crear_cuentas_demo(conexion)
    return _motor_defecto


def obtener_motor(request: Request) -> Engine:
    motor = getattr(request.app.state, "motor", None)
    if motor is None:
        motor = _obtener_motor_por_defecto()
    return motor


def obtener_conexion(motor: Engine = Depends(obtener_motor)) -> Generator[Connection, None, None]:
    # Las rutas pueden confirmar antes (chat guarda el mensaje del usuario aunque el modelo falle).
    with motor.connect() as conexion:
        yield conexion
        conexion.commit()


def obtener_resumidor() -> ProveedorLLM:
    # Se construye al pedir el resumen, no al arrancar: un error de configuración no tumba la API.
    return ProveedorDiferido(crear_resumidor)


@lru_cache
def obtener_cola() -> ColaPendientes:
    return ColaPendientes(obtener_configuracion().ruta_cola_pendientes)


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
