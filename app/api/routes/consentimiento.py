from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import obtener_usuario
from app.schemas.consentimiento import ConsentimientoEntrada, ConsentimientoSalida
from app.services.almacen import ahora, almacen

router = APIRouter(prefix="/consentimiento", tags=["consentimiento"])


@router.post(
    "",
    response_model=ConsentimientoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registra el consentimiento informado (RF-02)",
)
def registrar_consentimiento(
    entrada: ConsentimientoEntrada, usuario: dict = Depends(obtener_usuario)
) -> ConsentimientoSalida:
    if not (entrada.mayor_de_edad and entrada.acepta):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere ser mayor de edad y aceptar el consentimiento.",
        )
    fecha = ahora()
    almacen.consentimientos[usuario["id"]] = fecha
    return ConsentimientoSalida(usuario_id=usuario["id"], aceptado_en=fecha)
