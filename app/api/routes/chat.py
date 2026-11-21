import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Engine
from sqlalchemy.engine import Connection

from app.api.deps import (
    exigir_conversacion,
    obtener_cola,
    obtener_conexion,
    obtener_expresiones,
    obtener_motor,
    obtener_proveedor,
)
from app.repositorios.alertas import registrar_alerta
from app.repositorios.consentimiento import tiene_consentimiento
from app.repositorios.mensajes import buscar_mensaje_por_evento, guardar_mensaje, listar_mensajes
from app.schemas.chat import MensajeEntrada, MensajeHistorial, MensajeSalida
from app.services.almacen import ahora
from app.services.cola import ColaPendientes
from app.services.proveedor_llm import ProveedorLLM, ProveedorNoDisponible
from app.services.riesgo import RECURSOS_AYUDA, TEXTO_CRISIS, es_riesgo_alto
from app.services.sincronizador import SUFIJO_RESPUESTA

router = APIRouter(prefix="/chat", tags=["chat"])
registro = logging.getLogger(__name__)


@router.post(
    "",
    response_model=MensajeSalida,
    summary="Envía un mensaje al asistente (RF-07, RF-23, RF-24)",
)
def enviar_mensaje(
    entrada: MensajeEntrada,
    usuario: dict = Depends(exigir_conversacion),
    expresiones: tuple = Depends(obtener_expresiones),
    proveedor: ProveedorLLM = Depends(obtener_proveedor),
    motor: Engine = Depends(obtener_motor),
    cola: ColaPendientes = Depends(obtener_cola),
) -> MensajeSalida:
    fecha = ahora()
    id_evento = entrada.id_evento or uuid.uuid4().hex
    # La revisión de riesgo va primero y no necesita la base: la ayuda nunca depende de ella.
    if es_riesgo_alto(entrada.texto, expresiones):
        _registrar_crisis(motor, cola, usuario["id"], entrada.texto, fecha, id_evento)
        return MensajeSalida(
            tipo="crisis", texto=TEXTO_CRISIS, riesgo="alto", recursos=RECURSOS_AYUDA
        )
    return _responder(motor, usuario["id"], entrada.texto, fecha, id_evento, proveedor)


def _registrar_crisis(
    motor: Engine,
    cola: ColaPendientes,
    usuario_id: str,
    texto: str,
    fecha: datetime,
    id_evento: str,
) -> None:
    """Guarda la crisis en la base o, si no responde, en la cola local para sincronizar luego."""
    try:
        with motor.begin() as conexion:
            # Sin consentimiento no se guarda nada; la ayuda se muestra igual.
            if not tiene_consentimiento(conexion, usuario_id):
                return
            if buscar_mensaje_por_evento(conexion, usuario_id, id_evento) is not None:
                return  # reintento de un evento ya guardado
            guardar_mensaje(conexion, usuario_id, "usuario", "mensaje", texto, fecha, id_evento)
            registrar_alerta(conexion, usuario_id, "alto", texto, fecha, id_evento=id_evento)
            guardar_mensaje(
                conexion,
                usuario_id,
                "asistente",
                "crisis",
                TEXTO_CRISIS,
                ahora(),
                id_evento + SUFIJO_RESPUESTA,
            )
    except Exception as error:
        # Cualquier fallo de la base: la persona recibe la ayuda y el evento queda en la cola.
        registro.warning(
            "Base no disponible (%s): el evento de crisis queda en la cola local.",
            type(error).__name__,
        )
        cola.encolar(
            {
                "id_evento": id_evento,
                "usuario_id": usuario_id,
                "texto": texto,
                "fecha": fecha.isoformat(),
            }
        )


def _responder(
    motor: Engine,
    usuario_id: str,
    texto: str,
    fecha: datetime,
    id_evento: str,
    proveedor: ProveedorLLM,
) -> MensajeSalida:
    with motor.connect() as conexion:
        if not tiene_consentimiento(conexion, usuario_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debe aceptar el consentimiento antes de conversar.",
            )
        # Reintento: si la respuesta ya existe, se devuelve la misma, sin llamar al modelo.
        guardada = _respuesta_guardada(conexion, usuario_id, id_evento)
        if guardada is not None:
            return guardada

        if buscar_mensaje_por_evento(conexion, usuario_id, id_evento) is None:
            guardar_mensaje(conexion, usuario_id, "usuario", "mensaje", texto, fecha, id_evento)
            conexion.commit()  # el mensaje queda guardado aunque el modelo no responda

        fragmentos: list[tuple[str, str]] = []  # HU-08: búsqueda en el material aprobado.
        try:
            contenido = proveedor.responder(texto, fragmentos)
        except ProveedorNoDisponible as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El asistente no está disponible en este momento.",
            ) from error
        salida = MensajeSalida(
            tipo="respuesta", texto=contenido, riesgo="sin_riesgo", fragmentos=fragmentos
        )
        guardar_mensaje(
            conexion,
            usuario_id,
            "asistente",
            salida.tipo,
            salida.texto,
            ahora(),
            id_evento + SUFIJO_RESPUESTA,
        )
        conexion.commit()
        return salida


def _respuesta_guardada(
    conexion: Connection, usuario_id: str, id_evento: str
) -> MensajeSalida | None:
    fila = buscar_mensaje_por_evento(conexion, usuario_id, id_evento + SUFIJO_RESPUESTA)
    if fila is None:
        return None
    if fila["tipo"] == "crisis":
        return MensajeSalida(
            tipo="crisis", texto=fila["texto"], riesgo="alto", recursos=RECURSOS_AYUDA
        )
    return MensajeSalida(tipo="respuesta", texto=fila["texto"], riesgo="sin_riesgo")


@router.get(
    "/historial",
    response_model=list[MensajeHistorial],
    summary="Devuelve los mensajes anteriores del usuario (RF-07)",
)
def historial(
    usuario: dict = Depends(exigir_conversacion),
    conexion: Connection = Depends(obtener_conexion),
) -> list[dict]:
    return listar_mensajes(conexion, usuario["id"])
