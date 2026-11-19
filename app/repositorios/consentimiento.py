"""Repositorio del consentimiento (BE-03, HU-03).

Guarda la fecha en que cada cuenta acepto el consentimiento,
cada funcion recibe la conexion y la transaccion la abre quien llama.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as insertar_postgresql
from sqlalchemy.dialects.sqlite import insert as insertar_sqlite
from sqlalchemy.engine import Connection

from app.db import consentimientos

# Version del texto que se acepta. Es provisional hasta que entregue DOC-01
# y se haga la revision legal
VERSION_TEXTO_ACTUAL = "provisional-1"


def registrar_consentimiento(
    conexion: Connection,
    usuario_id: str,
    mayor_de_edad: bool,
    version_texto: str = VERSION_TEXTO_ACTUAL,
) -> datetime:
    """Guarda la aceptacion de la cuenta y devuelve la fecha registrada.
    Hay un solo registro por cuenta: una nueva aceptacion reemplaza la anterior.
    """
    fecha = datetime.now(timezone.utc)
    valores = {
        "version_texto": version_texto,
        "mayor_de_edad": mayor_de_edad,
        "aceptado_en": fecha,
    }
    # Una sola sentencia resuelve también dos primeras aceptaciones simultáneas.
    if conexion.dialect.name == "postgresql":
        insertar = insertar_postgresql
    elif conexion.dialect.name == "sqlite":
        insertar = insertar_sqlite
    else:
        raise ValueError("El consentimiento requiere PostgreSQL o SQLite.")
    sentencia = insertar(consentimientos).values(usuario_id=usuario_id, **valores)
    conexion.execute(
        sentencia.on_conflict_do_update(index_elements=[consentimientos.c.usuario_id], set_=valores)
    )
    return fecha


def buscar_fecha_aceptacion(conexion: Connection, usuario_id: str) -> datetime | None:
    """Devuelve la fecha en que la cuenta aceptó, o None si nunca aceptó."""
    fecha = conexion.execute(
        select(consentimientos.c.aceptado_en).where(consentimientos.c.usuario_id == usuario_id)
    ).scalar()
    if fecha is not None and fecha.tzinfo is None:
        # SQLite no guarda la zona horaria en cambio PostgreSQL si entonces se normaliza a UTC.
        fecha = fecha.replace(tzinfo=timezone.utc)
    return fecha


def tiene_consentimiento(conexion: Connection, usuario_id: str) -> bool:
    """True si la cuenta ya aceptó el consentimiento."""
    return buscar_fecha_aceptacion(conexion, usuario_id) is not None


guardar_consentimiento = registrar_consentimiento
