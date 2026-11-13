from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MensajeEntrada(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)


class Recurso(BaseModel):
    nombre: str
    telefono: str
    descripcion: str


class MensajeSalida(BaseModel):
    tipo: Literal["respuesta", "crisis"]
    texto: str
    riesgo: Literal["sin_riesgo", "alto"]
    fragmentos: list[str] = []
    recursos: list[Recurso] = []


class MensajeHistorial(BaseModel):
    autor: Literal["usuario", "asistente"]
    texto: str
    fecha: datetime
    tipo: Literal["mensaje", "respuesta", "crisis"]
