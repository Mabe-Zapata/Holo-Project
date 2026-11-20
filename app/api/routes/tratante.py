from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.engine import Connection

from app.api.deps import obtener_cola, obtener_conexion, obtener_usuario
from app.repositorios.alertas import listar_alertas
from app.repositorios.usuarios import buscar_usuario
from app.repositorios.vinculos import buscar_paciente_vinculado
from app.schemas.tratante import VistaPaciente
from app.services.cola import ColaPendientes

router = APIRouter(prefix="/tratante", tags=["tratante"])


@router.get(
    "/paciente",
    response_model=VistaPaciente,
    summary="Devuelve las alertas y el último resumen del paciente vinculado (RF-25, RF-30)",
)
def vista_paciente(
    usuario: dict = Depends(obtener_usuario),
    conexion: Connection = Depends(obtener_conexion),
    cola: ColaPendientes = Depends(obtener_cola),
) -> VistaPaciente:
    if usuario["rol"] != "tratante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el tratante puede consultar esta vista.",
        )
    # Solo el paciente con vínculo activo con este tratante; otro tratante recibe 403.
    paciente_id = buscar_paciente_vinculado(conexion, usuario["id"])
    if paciente_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes un paciente vinculado.",
        )
    paciente = buscar_usuario(conexion, paciente_id)
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    return VistaPaciente(
        paciente_id=paciente_id,
        nombre=paciente["nombre"],
        alertas=listar_alertas(conexion, paciente_id),
        alertas_pendientes=sum(1 for e in cola.pendientes() if e["usuario_id"] == paciente_id),
        resumen=None,  # HU-17
    )
