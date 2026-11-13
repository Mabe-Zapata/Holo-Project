"""Punto de entrada de la API de Holo."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, consentimiento, resumen, salud, tratante
from app.core.config import obtener_configuracion


def crear_app() -> FastAPI:
    cfg = obtener_configuracion()
    app = FastAPI(
        title=cfg.nombre_app,
        version=cfg.version,
        description=(
            "API del proyecto Holo. Versión de demostración: usa cuentas "
            "ficticias y almacenamiento en memoria."
        ),
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
