"""Recuperación de fragmentos del material para una consulta (HU-08a).

Puntúa cada texto por la proporción de palabras de la consulta que aparecen en él.
Solo usa la biblioteca estándar. Devuelve como mucho tres fragmentos, y ninguno si
ninguno supera el umbral. El umbral y los filtros de visibilidad los define el equipo.
"""

import re

from app.services.riesgo import normalizar

MAXIMO_FRAGMENTOS = 3
UMBRAL_RELEVANCIA = 0.5

# Palabras que no distinguen un tema. Lista corta, provisional.
PALABRAS_VACIAS = frozenset(
    """
    al algo como con cuando de del desde el ella ellas ellos en era es esa ese esta este esto
    estoy eso la las le les lo los mas me mi mis muy no o para pero por que se si sin son soy
    su sus te tengo tiene tu tus un una unas unos ya hay ser he ha puedo puede mucho mucha
    """.split()
)


def palabras(texto: str) -> set[str]:
    """Palabras significativas, en minúsculas y sin tildes."""
    return {p for p in re.findall(r"[a-z0-9]+", normalizar(texto)) if len(p) > 2} - PALABRAS_VACIAS


def es_visible(texto: dict, modo: str) -> bool:
    """El material de modo paciente o del módulo de ansiedad solo llega a cuentas de paciente."""
    if texto["modo"] == "paciente" and modo != "paciente":
        return False
    if texto["modulo"] == "ansiedad" and modo != "paciente":
        return False
    return True


def buscar_fragmentos(
    consulta: str,
    textos: list[dict],
    modo: str,
    umbral: float = UMBRAL_RELEVANCIA,
    maximo: int = MAXIMO_FRAGMENTOS,
) -> list[tuple[str, str]]:
    """Devuelve (id, texto) de los textos más pertinentes a la consulta."""
    pregunta = palabras(consulta)
    if not pregunta:
        return []
    puntuados = []
    for texto in textos:
        if not es_visible(texto, modo):
            continue
        contenido = palabras(f"{texto['titulo']} {texto['tema']} {texto['texto']}")
        puntaje = len(pregunta & contenido) / len(pregunta)
        if puntaje >= umbral:
            puntuados.append((-puntaje, texto["id"], texto["texto"]))
    puntuados.sort()
    return [(id_, contenido) for _, id_, contenido in puntuados[:maximo]]
