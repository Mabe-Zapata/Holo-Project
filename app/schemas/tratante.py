from datetime import datetime

from pydantic import BaseModel


class Alerta(BaseModel):
    nivel: str
    mensaje: str
    fecha: datetime


class VistaPaciente(BaseModel):
    paciente_id: str
    nombre: str
    alertas: list[Alerta]
    # Alertas que aún no llegaron a la base y se están sincronizando.
    alertas_pendientes: int = 0
    resumen: str | None = None
