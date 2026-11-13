from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import obtener_usuario

router = APIRouter(prefix="/resumen", tags=["resumen"])


@router.post("", summary="Genera el resumen de los últimos siete días (RF-19)")
def generar_resumen(usuario: dict = Depends(obtener_usuario)) -> dict:
    if usuario["rol"] != "tratante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el tratante puede generar el resumen.",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Pendiente de implementar: historia HU-17.",
    )
