"""Almacenamiento en memoria para la demostración.

Se reemplaza por SQLite en la historia HU-06. Los datos se pierden al
reiniciar el servidor.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

# Cuentas de demostración (RF-03). No hay registro ni contraseñas en el MVP.
CUENTAS_DEMO: dict[str, dict] = {
    "ana": {"nombre": "Ana", "rol": "usuario_estandar", "tratante_id": None},
    "luis": {"nombre": "Luis", "rol": "paciente", "tratante_id": "tratante"},
    "tratante": {"nombre": "Tratante de demostración", "rol": "tratante", "tratante_id": None},
}


@dataclass
class Almacen:
    consentimientos: dict[str, datetime] = field(default_factory=dict)
    mensajes: dict[str, list[dict]] = field(default_factory=dict)
    alertas: dict[str, list[dict]] = field(default_factory=dict)

    def reiniciar(self) -> None:
        self.consentimientos.clear()
        self.mensajes.clear()
        self.alertas.clear()


almacen = Almacen()


def ahora() -> datetime:
    return datetime.now(timezone.utc)
