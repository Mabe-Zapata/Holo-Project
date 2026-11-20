"""Vínculos entre paciente y tratante (HU-16, HU-18)."""

from sqlalchemy import select
from sqlalchemy.engine import Connection

from app.db import vinculos


def buscar_paciente_vinculado(conexion: Connection, profesional_id: str) -> str | None:
    """Devuelve el id del paciente con vínculo activo con este tratante, o None."""
    return conexion.execute(
        select(vinculos.c.paciente_id)
        .where(vinculos.c.profesional_id == profesional_id, vinculos.c.estado == "activo")
        .order_by(vinculos.c.id)
        .limit(1)
    ).scalar()
