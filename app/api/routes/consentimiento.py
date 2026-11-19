from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.engine import Connection

from app.api.deps import obtener_conexion, obtener_usuario
from app.repositorios.consentimiento import (
    registrar_consentimiento as guardar_consentimiento,
)
from app.schemas.consentimiento import (
    ConsentimientoEntrada,
    ConsentimientoSalida,
)

router = APIRouter(prefix="/consentimiento", tags=["consentimiento"])


@router.post(
    "",
    response_model=ConsentimientoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registra el consentimiento informado (BE-03, HU-03)",
)
def registrar_consentimiento(
    entrada: ConsentimientoEntrada,
    usuario: dict = Depends(obtener_usuario),
    conexion: Connection = Depends(obtener_conexion),
) -> ConsentimientoSalida:

    if not (entrada.mayor_de_edad and entrada.acepta):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere ser mayor de edad y aceptar el consentimiento.",
        )

    fecha = guardar_consentimiento(
        conexion=conexion,
        usuario_id=usuario["id"],
        mayor_de_edad=entrada.mayor_de_edad,
    )

    return ConsentimientoSalida(
        usuario_id=usuario["id"],
        aceptado_en=fecha,
    )
