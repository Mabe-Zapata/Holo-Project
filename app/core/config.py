"""Configuración leída de variables de entorno (prefijo HOLO_) o del archivo .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="HOLO_", extra="ignore")

    nombre_app: str = "Holo API"
    version: str = "0.1.0"
    entorno: str = "desarrollo"
    # Proveedor del modelo de lenguaje. "eco" no usa ningún modelo (HU-09).
    proveedor_llm: str = "eco"
    llm_api_key: str = ""
    # Orígenes permitidos para CORS, separados por coma.
    origenes_cors: str = "*"
    ruta_expresiones_riesgo: str = "data/expresiones_riesgo.txt"


@lru_cache
def obtener_configuracion() -> Configuracion:
    return Configuracion()
