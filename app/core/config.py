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
    # Modelo y dirección de la API compatible con OpenAI (HU-09).
    # Verificar el nombre del modelo en la consola del proveedor.
    llm_modelo: str = ""
    llm_url_base: str = "https://api.groq.com/openai/v1"
    # Orígenes permitidos para CORS, separados por coma.
    origenes_cors: str = "*"
    # Nivel de los registros del código de Holo (BE-15). Las bibliotecas quedan en WARNING.
    nivel_registros: str = "INFO"
    ruta_expresiones_riesgo: str = "data/expresiones_riesgo.txt"
    # Conexión a PostgreSQL con SQLAlchemy (BE-01). Se define en .env.
    url_base_datos: str = "postgresql+psycopg://holo:cambiar_esta_clave@localhost:5432/holo"
    # Estados del material que el asistente puede usar (HU-08b). Por defecto solo el aprobado.
    estados_material: str = "aprobado"
    # Cola local de eventos de crisis que no pudieron guardarse en la base (HU-16).
    ruta_cola_pendientes: str = "data/cola/pendientes.jsonl"
    # Reintento automático de la cola en segundo plano y su intervalo en segundos.
    sincronizar_automaticamente: bool = True
    intervalo_sincronizacion_s: float = 15.0


@lru_cache
def obtener_configuracion() -> Configuracion:
    return Configuracion()
