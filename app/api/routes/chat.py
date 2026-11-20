from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.engine import Connection

from app.api.deps import (
    exigir_conversacion,
    obtener_conexion,
    obtener_expresiones,
    obtener_proveedor,
)
from app.repositorios.consentimiento import tiene_consentimiento
from app.repositorios.mensajes import guardar_mensaje, listar_mensajes
from app.schemas.chat import MensajeEntrada, MensajeHistorial, MensajeSalida
from app.services.almacen import ahora, almacen
from app.services.proveedor_llm import ProveedorLLM, ProveedorNoDisponible
from app.services.riesgo import RECURSOS_AYUDA, TEXTO_CRISIS, es_riesgo_alto

router = APIRouter(prefix="/chat", tags=["chat"])


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
    conexion: Connection = Depends(obtener_conexion),
) -> MensajeSalida:
    if not tiene_consentimiento(conexion, usuario["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe aceptar el consentimiento antes de conversar.",
        )

    fecha = ahora()
    guardar_mensaje(conexion, usuario["id"], "usuario", "mensaje", entrada.texto, fecha)
    # El mensaje del usuario queda guardado aunque el modelo no responda.
    conexion.commit()

    # La revisión de riesgo ocurre siempre antes de consultar al modelo.
    if es_riesgo_alto(entrada.texto, expresiones):
        almacen.alertas.setdefault(usuario["id"], []).append(
            {"nivel": "alto", "mensaje": entrada.texto, "fecha": fecha}
        )
        salida = MensajeSalida(
            tipo="crisis", texto=TEXTO_CRISIS, riesgo="alto", recursos=RECURSOS_AYUDA
        )
    else:
        fragmentos: list[tuple[str, str]] = []  # HU-08: búsqueda en el material aprobado.
        try:
            texto = proveedor.responder(entrada.texto, fragmentos)
        except ProveedorNoDisponible as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El asistente no está disponible en este momento.",
            ) from error
        salida = MensajeSalida(
            tipo="respuesta", texto=texto, riesgo="sin_riesgo", fragmentos=fragmentos
        )

    guardar_mensaje(conexion, usuario["id"], "asistente", salida.tipo, salida.texto, ahora())
    conexion.commit()
    return salida


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
