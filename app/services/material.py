"""Validación del material etiquetado (HU-07).

Las etiquetas y los estados los define la especialista. Un texto sin etiquetas
válidas no entra a la base.
"""

from app.repositorios.material import CAMPOS

MODULOS = ("general", "ansiedad", "sueno")
MODOS = ("estandar", "paciente")
ESTADOS = ("provisional", "aprobado")
MINIMO_LOTE = 5
MAXIMO_LOTE = 10


def validar_texto(datos: dict) -> dict:
    """Devuelve el texto con sus campos limpios o lanza ValueError con el motivo."""
    if not isinstance(datos, dict):
        raise ValueError("Cada texto debe ser un objeto JSON.")
    faltan = [campo for campo in CAMPOS if campo not in datos]
    if faltan:
        raise ValueError(f"Al texto le faltan campos: {', '.join(faltan)}.")
    limpio = {}
    for campo in CAMPOS:
        valor = datos[campo]
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"El campo '{campo}' debe ser texto no vacío.")
        limpio[campo] = valor.strip()
    if limpio["modulo"] not in MODULOS:
        raise ValueError(f"Módulo no válido: {limpio['modulo']}.")
    if limpio["modo"] not in MODOS:
        raise ValueError(f"Modo no válido: {limpio['modo']}.")
    if limpio["estado"] not in ESTADOS:
        raise ValueError(f"Estado no válido: {limpio['estado']}.")
    if limpio["modulo"] == "ansiedad" and limpio["modo"] != "paciente":
        raise ValueError("El material del módulo de ansiedad solo puede ser de modo paciente.")
    return limpio


def validar_lote(textos: list) -> list[dict]:
    """Valida un lote completo. HU-07 pide entre 5 y 10 textos por carga."""
    if not isinstance(textos, list):
        raise ValueError("El archivo debe contener una lista de textos.")
    if not MINIMO_LOTE <= len(textos) <= MAXIMO_LOTE:
        raise ValueError(f"Cada carga debe tener entre {MINIMO_LOTE} y {MAXIMO_LOTE} textos.")
    ids = [t.get("id") for t in textos if isinstance(t, dict)]
    if len(set(ids)) != len(ids):
        raise ValueError("Hay identificadores repetidos en el lote.")
    return [validar_texto(t) for t in textos]
