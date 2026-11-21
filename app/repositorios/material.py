"""Repositorio del material etiquetado (HU-07).

Cada función recibe la conexión y la transacción la abre quien llama.
"""

from sqlalchemy import select, update
from sqlalchemy.engine import Connection

from app.db import material

CAMPOS = ("id", "titulo", "tema", "modulo", "modo", "estado", "fuente", "texto")


def guardar_texto(conexion: Connection, datos: dict) -> None:
    """Crea el texto o, si ya existe con ese id, lo actualiza. Es idempotente."""
    valores = {campo: datos[campo] for campo in CAMPOS}
    existe = conexion.execute(select(material.c.id).where(material.c.id == datos["id"])).first()
    if existe is None:
        conexion.execute(material.insert().values(**valores))
    else:
        conexion.execute(update(material).where(material.c.id == datos["id"]).values(**valores))


def listar_textos(conexion: Connection, estados: tuple[str, ...]) -> list[dict]:
    """Textos cuyo estado está en `estados`, ordenados por id."""
    filas = conexion.execute(
        select(*(material.c[campo] for campo in CAMPOS))
        .where(material.c.estado.in_(estados))
        .order_by(material.c.id)
    ).mappings()
    return [dict(fila) for fila in filas]
