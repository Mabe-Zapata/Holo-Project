"""Revisión de riesgo por lista de expresiones (RF-23) y texto de crisis (RF-24).

La lista de expresiones y el texto de crisis los define y aprueba la
especialista. Lo que hay aquí es provisional.
"""

import unicodedata
from pathlib import Path

TEXTO_CRISIS = (
    "[Texto provisional, pendiente de aprobación de la especialista] "
    "Lo que estás viviendo importa y no tienes que enfrentarlo a solas. "
    "Si estás en peligro ahora, llama al ECU 911. También puedes llamar a la "
    "línea 171, opción 6, del Ministerio de Salud Pública."
)

RECURSOS_AYUDA = [
    {"nombre": "ECU 911", "telefono": "911", "descripcion": "Emergencias"},
    {
        "nombre": "Línea 171, opción 6",
        "telefono": "171",
        "descripcion": "Salud mental, Ministerio de Salud Pública",
    },
]


def normalizar(texto: str) -> str:
    """Pasa a minúsculas y quita tildes para comparar sin diferencias de escritura."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())


def cargar_expresiones(ruta: str) -> list[str]:
    """Lee una expresión por línea; ignora líneas vacías y comentarios (#)."""
    archivo = Path(ruta)
    if not archivo.exists():
        return []
    expresiones = []
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            expresiones.append(normalizar(linea))
    return expresiones


def es_riesgo_alto(mensaje: str, expresiones) -> bool:
    texto = normalizar(mensaje)
    return any(expresion in texto for expresion in expresiones)
