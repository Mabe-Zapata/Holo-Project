"""Filtro de consultas clínicas (HU-10): el asistente no opina sobre diagnósticos ni medicación.

Los patrones y la respuesta fija los define y aprueba la especialista.
Lo que hay aquí es provisional.
"""

import re

from app.services.riesgo import normalizar

RESPUESTA_CLINICA = (
    "[Texto provisional, pendiente de aprobación de la especialista] "
    "Los diagnósticos y la medicación los decide un profesional de salud. "
    "Te recomiendo consultarlo con tu tratante o con tu médico."
)

# Se buscan sobre el texto normalizado (minúsculas y sin tildes).
PATRONES_CLINICOS = [
    r"\bdiagnostic\w*",
    r"\bmedicac\w*",
    r"\bmedicament\w*",
    r"\bpastillas?\b",
    r"\bdosis\b",
    r"\bmiligramos\b|\bmg\b",
    r"\bantidepresiv\w*",
    r"\bansiolitic\w*",
    r"\bantipsicotic\w*",
    r"\brecetar\w*|\breceta medica\b",
    r"\btrastorno\w*",
    r"\btengo (depresion|bipolaridad|tdah)\b",
    (
        r"\b(dejar|suspender|subir|bajar|aumentar|reducir) (de )?(la |el |mi |mis )?"
        r"(dosis|medicacion|medicamento|tratamiento|pastillas)\b"
    ),
]

_PATRON = re.compile("|".join(f"(?:{p})" for p in PATRONES_CLINICOS))


def es_consulta_clinica(texto: str) -> bool:
    return _PATRON.search(normalizar(texto)) is not None
