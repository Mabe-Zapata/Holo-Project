from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import obtener_usuario
from app.schemas.tratante import VistaPaciente
from app.services.almacen import CUENTAS_DEMO, almacen

router = APIRouter(prefix="/tratante", tags=["tratante"])


@router.get(
    "/paciente",
    response_model=VistaPaciente,
    summary="Devuelve las alertas y el último resumen del paciente vinculado (RF-25, RF-30)",
)
def vista_paciente(usuario: dict = Depends(obtener_usuario)) -> VistaPaciente:
    if usuario["rol"] != "tratante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el tratante puede consultar esta vista.",
        )
    # En el MVP hay un único paciente vinculado al tratante de demostración.
    paciente_id = next(
        (pid for pid, c in CUENTAS_DEMO.items() if c["tratante_id"] == usuario["id"]), None
    )
    if paciente_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sin pacientes vinculados."
        )
    return VistaPaciente(
        paciente_id=paciente_id,
        nombre=CUENTAS_DEMO[paciente_id]["nombre"],
        alertas=almacen.alertas.get(paciente_id, []),
        resumen=None,  # HU-17
    )
