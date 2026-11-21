"""Repositorio de las alertas de riesgo (HU-16).

Cada función recibe la conexión y la transacción la abre quien llama.
"""

from datetime import datetime, timezone

from sqlalchemy import insert, select
from sqlalchemy.engine import Connection

from app.db import alertas

NIVELES = ("alto",)


def registrar_alerta(
    conexion: Connection,
    usuario_id: str,
    nivel: str,
    mensaje: str,
    creado_en: datetime,
    id_evento: str | None = None,
) -> None:
    """Guarda una situación de riesgo. Rechaza niveles desconocidos y mensajes vacíos."""
    if nivel not in NIVELES:
        raise ValueError(f"Nivel de alerta no soportado: {nivel}")
    if not mensaje.strip():
        raise ValueError("La alerta necesita el mensaje que la originó.")
    conexion.execute(
        insert(alertas).values(
            usuario_id=usuario_id,
            nivel=nivel,
            mensaje=mensaje,
            creado_en=creado_en,
            id_evento=id_evento,
        )
    )


def listar_alertas(conexion: Connection, usuario_id: str) -> list[dict]:
    """Devuelve las alertas de la cuenta en orden cronológico (la más antigua primero)."""
    filas = conexion.execute(
        select(alertas.c.nivel, alertas.c.mensaje, alertas.c.creado_en)
        .where(alertas.c.usuario_id == usuario_id)
        .order_by(alertas.c.creado_en, alertas.c.id)
    ).all()
    return [
        {"nivel": f.nivel, "mensaje": f.mensaje, "fecha": _con_zona_horaria(f.creado_en)}
        for f in filas
    ]


def _con_zona_horaria(fecha: datetime) -> datetime:
    # SQLite no guarda la zona horaria; PostgreSQL sí. Se normaliza a UTC.
    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha
