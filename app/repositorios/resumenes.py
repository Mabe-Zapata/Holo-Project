"""Repositorio de los resúmenes semanales (HU-17b).

Cada función recibe la conexión y la transacción la abre quien llama.
"""

from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.engine import Connection

from app.db import resumenes


def guardar_resumen(
    conexion: Connection, paciente_id: str, generado_en: datetime, contenido: dict
) -> None:
    conexion.execute(
        insert(resumenes).values(
            paciente_id=paciente_id, generado_en=generado_en, contenido=contenido
        )
    )


def ultimo_resumen(conexion: Connection, paciente_id: str) -> dict | None:
    """El resumen más reciente del paciente, o None si nunca se generó uno."""
    return conexion.execute(
        select(resumenes.c.contenido)
        .where(resumenes.c.paciente_id == paciente_id)
        .order_by(resumenes.c.generado_en.desc(), resumenes.c.id.desc())
        .limit(1)
    ).scalar()
