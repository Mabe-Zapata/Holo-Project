import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Engine

from app.api.deps import obtener_motor, obtener_resumidor, obtener_usuario
from app.repositorios.alertas import listar_alertas
from app.repositorios.mensajes import listar_mensajes
from app.repositorios.resumenes import guardar_resumen
from app.repositorios.vinculos import buscar_paciente_vinculado
from app.services.almacen import ahora
from app.services.proveedor_llm import ProveedorLLM, ProveedorNoDisponible
from app.services.resumen import (
    ResumenNoValido,
    alertas_del_periodo,
    generar_resumen,
    mensajes_de_la_semana,
    periodo,
)

router = APIRouter(prefix="/resumen", tags=["resumen"])
registro = logging.getLogger(__name__)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Genera el resumen de los últimos siete días del paciente vinculado (RF-19, HU-17)",
)
def generar_resumen_semanal(
    usuario: dict = Depends(obtener_usuario),
    motor: Engine = Depends(obtener_motor),
    resumidor: ProveedorLLM = Depends(obtener_resumidor),
) -> dict:
    if usuario["rol"] != "tratante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el tratante puede generar el resumen.",
        )
    momento = ahora()
    desde, hasta = periodo(momento)
    with motor.connect() as conexion:
        paciente_id = buscar_paciente_vinculado(conexion, usuario["id"])
        if paciente_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes un paciente vinculado.",
            )
        mensajes = mensajes_de_la_semana(listar_mensajes(conexion, paciente_id), momento)
        try:
            resultado = generar_resumen(mensajes, resumidor)
        except ProveedorNoDisponible as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El asistente no está disponible en este momento.",
            ) from error
        except ResumenNoValido as error:
            registro.warning("El modelo no devolvió un resumen válido.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="El resumen no pudo generarse. Inténtalo de nuevo.",
            ) from error

        respuesta = {
            "paciente_id": paciente_id,
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat(),
            "generado_en": momento.isoformat(),
            "generado_por_ia": True,
            "temas": resultado["temas"],
            "hechos": resultado["hechos"],
            "patrones": resultado["patrones"],
            "alertas": alertas_del_periodo(listar_alertas(conexion, paciente_id), desde, hasta),
        }
        guardar_resumen(conexion, paciente_id, momento, respuesta)
        conexion.commit()
    return respuesta
