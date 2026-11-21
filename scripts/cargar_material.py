"""Carga el material etiquetado en la base (HU-07).

Uso (desde la raíz del repositorio):
    python scripts/cargar_material.py data/material/textos_iniciales.json

Es idempotente: volver a cargar el mismo archivo actualiza los textos, no los duplica.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from sqlalchemy import Engine  # noqa: E402

from app.db import crear_motor, crear_tablas  # noqa: E402
from app.repositorios.material import guardar_texto  # noqa: E402
from app.services.material import validar_lote  # noqa: E402


def cargar_desde_archivo(motor: Engine, ruta: Path) -> int:
    """Valida el archivo completo y luego lo guarda en una sola transacción."""
    textos = validar_lote(json.loads(ruta.read_text(encoding="utf-8")))
    crear_tablas(motor)
    with motor.begin() as conexion:
        for texto in textos:
            guardar_texto(conexion, texto)
    return len(textos)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/cargar_material.py <archivo.json>")
    cantidad = cargar_desde_archivo(crear_motor(), Path(sys.argv[1]))
    print(f"Se cargaron {cantidad} textos de material.")
