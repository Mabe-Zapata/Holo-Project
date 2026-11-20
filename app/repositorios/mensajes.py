"""Repositorio de mensajes del chat (BE-04).

Guarda y lista los mensajes de cada usuario. Como el resto de los repositorios, cada función
recibe la conexión y la transacción la abre quien llama, por ejemplo con `motor.begin()`.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.engine import Connection

from app.db import mensajes


def guardar_mensaje(
    conexion: Connection,
    usuario_id: str,
    autor: str,
    tipo: str,
    texto: str,
    fecha: datetime | None = None,
    id_evento: str | None = None,
    fragmentos: list[str] | None = None,
) -> None:
    """Guarda un mensaje con fecha normalizada a UTC.

    Sin fecha usa la hora actual. Una fecha sin zona se interpreta como UTC,
    sin consultar la zona del equipo que ejecuta la aplicación. Con `id_evento`, un
    segundo mensaje con el mismo identificador para la misma cuenta se rechaza.
    """
    fecha_utc = fecha if fecha is not None else datetime.now(timezone.utc)
    if fecha_utc.utcoffset() is None:
        fecha_utc = fecha_utc.replace(tzinfo=timezone.utc)
    else:
        fecha_utc = fecha_utc.astimezone(timezone.utc)
    # La fecha opcional permite cargar las conversaciones de Luis con su día de origen (BE-07b).
    conexion.execute(
        mensajes.insert().values(
            usuario_id=usuario_id,
            autor=autor,
            tipo=tipo,
            texto=texto,
            creado_en=fecha_utc,
            id_evento=id_evento,
            fragmentos=fragmentos,
        )
    )


def buscar_mensaje_por_evento(conexion: Connection, usuario_id: str, id_evento: str) -> dict | None:
    """Devuelve el mensaje guardado con ese identificador de evento, o None."""
    fila = (
        conexion.execute(
            select(
                mensajes.c.autor, mensajes.c.tipo, mensajes.c.texto, mensajes.c.fragmentos
            ).where(mensajes.c.usuario_id == usuario_id, mensajes.c.id_evento == id_evento)
        )
        .mappings()
        .first()
    )
    return dict(fila) if fila is not None else None


def listar_mensajes(conexion: Connection, usuario_id: str) -> list[dict]:
    """Devuelve los mensajes del usuario en orden cronológico.

    Cada mensaje tiene las claves de MensajeHistorial y de GET /chat/historial:
    autor, texto, fecha y tipo. Con la misma fecha se respeta el orden de inserción.
    """
    filas = conexion.execute(
        select(mensajes.c.autor, mensajes.c.texto, mensajes.c.creado_en, mensajes.c.tipo)
        .where(mensajes.c.usuario_id == usuario_id)
        .order_by(mensajes.c.creado_en, mensajes.c.id)
    )
    return [
        {"autor": f.autor, "texto": f.texto, "fecha": f.creado_en, "tipo": f.tipo} for f in filas
    ]
