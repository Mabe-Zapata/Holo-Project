from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import obtener_expresiones, obtener_proveedor, obtener_usuario
from app.schemas.chat import MensajeEntrada, MensajeHistorial, MensajeSalida
from app.services.almacen import ahora, almacen
from app.services.proveedor_llm import ProveedorLLM
from app.services.riesgo import RECURSOS_AYUDA, TEXTO_CRISIS, es_riesgo_alto

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=MensajeSalida,
    summary="Envía un mensaje al asistente (RF-07, RF-23, RF-24)",
)
def enviar_mensaje(
    entrada: MensajeEntrada,
    usuario: dict = Depends(obtener_usuario),
    expresiones: tuple = Depends(obtener_expresiones),
    proveedor: ProveedorLLM = Depends(obtener_proveedor),
) -> MensajeSalida:
    if usuario["id"] not in almacen.consentimientos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe aceptar el consentimiento antes de conversar.",
        )

    historial = almacen.mensajes.setdefault(usuario["id"], [])
    fecha = ahora()
    historial.append(
        {"autor": "usuario", "texto": entrada.texto, "fecha": fecha, "tipo": "mensaje"}
    )

    # La revisión de riesgo ocurre siempre antes de consultar al modelo.
    if es_riesgo_alto(entrada.texto, expresiones):
        almacen.alertas.setdefault(usuario["id"], []).append(
            {"nivel": "alto", "mensaje": entrada.texto, "fecha": fecha}
        )
        salida = MensajeSalida(
            tipo="crisis", texto=TEXTO_CRISIS, riesgo="alto", recursos=RECURSOS_AYUDA
        )
    else:
        fragmentos: list[str] = []  # HU-08: búsqueda en el material aprobado.
        texto = proveedor.responder(entrada.texto, fragmentos)
        salida = MensajeSalida(
            tipo="respuesta", texto=texto, riesgo="sin_riesgo", fragmentos=fragmentos
        )

    historial.append(
        {"autor": "asistente", "texto": salida.texto, "fecha": ahora(), "tipo": salida.tipo}
    )
    return salida


@router.get(
    "/historial",
    response_model=list[MensajeHistorial],
    summary="Devuelve los mensajes anteriores del usuario (RF-07)",
)
def historial(usuario: dict = Depends(obtener_usuario)) -> list[dict]:
    return almacen.mensajes.get(usuario["id"], [])
