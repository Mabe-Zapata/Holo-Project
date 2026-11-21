from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

LIMITE_TEXTO = 2000


class MensajeEntrada(BaseModel):
    texto: str = Field(min_length=1, max_length=LIMITE_TEXTO)
    # Identificador que el cliente pone a cada mensaje: reintentar con el mismo id no duplica.
    id_evento: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{8,64}$")

    @field_validator("texto", mode="before")
    @classmethod
    def validar_texto(cls, texto):
        if isinstance(texto, str):
            if not texto.strip():
                raise PydanticCustomError("texto_vacio", "El mensaje no puede estar vacío.")
            if len(texto) > LIMITE_TEXTO:
                raise PydanticCustomError(
                    "texto_largo",
                    "El mensaje no puede superar los 2000 caracteres.",
                )
        return texto


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
