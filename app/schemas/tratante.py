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
    resumen: str | None = None
