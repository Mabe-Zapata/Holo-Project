"""Punto de entrada de la API de Holo."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, consentimiento, resumen, salud, tratante
from app.core.config import obtener_configuracion
from app.core.logging import configurar_registros
from app.db import crear_motor, crear_tablas
from app.repositorios.usuarios import crear_cuentas_demo


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Al iniciar, crea las tablas que falten en la base (BE-01).
    motor = crear_motor()
    app.state.motor = motor 
    crear_tablas(motor)
    # Crea las cuentas de demostración que falten (BE-02).
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
    yield
    motor.dispose()


def crear_app() -> FastAPI:
    cfg = obtener_configuracion()
    configurar_registros(cfg.nivel_registros)
    app = FastAPI(
        title=cfg.nombre_app,
        version=cfg.version,
        description=(
            "API del proyecto Holo. Versión de demostración: usa cuentas "
            "ficticias y almacenamiento en memoria."
        ),
        lifespan=ciclo_de_vida,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in cfg.origenes_cors.split(",")],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(salud.router)
    app.include_router(consentimiento.router)
    app.include_router(chat.router)
    app.include_router(resumen.router)
    app.include_router(tratante.router)
    return app


app = crear_app()
