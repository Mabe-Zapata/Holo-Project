from datetime import datetime

from pydantic import BaseModel


class ConsentimientoEntrada(BaseModel):
    mayor_de_edad: bool
    acepta: bool


class ConsentimientoSalida(BaseModel):
    usuario_id: str
    aceptado_en: datetime
