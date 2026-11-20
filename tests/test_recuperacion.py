"""Recuperación de fragmentos del material (HU-08a).

La tabla de consultas documenta lo que devuelve el recuperador con el material inicial.
Si cambian los textos o el umbral, esta tabla debe actualizarse con el nuevo resultado.
"""

import json
from pathlib import Path

import pytest

from app.services.recuperacion import MAXIMO_FRAGMENTOS, buscar_fragmentos, es_visible, palabras

RAIZ = Path(__file__).resolve().parent.parent
TEXTOS = json.loads((RAIZ / "data" / "material" / "textos_iniciales.json").read_text("utf-8"))

# (consulta, modo, ids esperados). Resultados observados con el umbral de 0.5.
CONSULTAS = [
    ("Tengo ansiedad y no puedo dormir", "paciente", ["M-01", "M-05"]),
    ("Tengo ansiedad y no puedo dormir", "estandar", ["M-05"]),
    ("respiracion para el estres", "paciente", ["M-01", "M-02", "M-06"]),
    ("cuando pedir ayuda", "paciente", ["M-07", "M-01"]),
    ("dormir mejor por las noches", "estandar", ["M-05"]),
    ("necesito pausas en mi dia", "estandar", ["M-06"]),
    ("como respirar cuando estoy nerviosa", "paciente", ["M-02"]),
    ("como respirar cuando estoy nerviosa", "estandar", []),
    ("anclaje 5 4 3 2 1", "paciente", ["M-03"]),
    ("hola que tal", "paciente", []),
]


@pytest.mark.parametrize("consulta, modo, esperados", CONSULTAS)
def test_las_consultas_documentadas_devuelven_lo_esperado(consulta, modo, esperados):
    ids = [id_ for id_, _ in buscar_fragmentos(consulta, TEXTOS, modo)]

    assert ids == esperados


def test_una_consulta_sin_palabras_utiles_no_devuelve_nada():
    assert palabras("¿y eso?") == set()
    assert buscar_fragmentos("¿y eso?", TEXTOS, "paciente") == []


def test_se_devuelven_como_mucho_tres_fragmentos():
    textos = [
        {
            "id": f"X-{n}",
            "titulo": "x",
            "tema": "x",
            "modulo": "general",
            "modo": "estandar",
            "texto": "ansiedad dormir respirar",
        }
        for n in range(6)
    ]

    resultado = buscar_fragmentos("ansiedad dormir respirar", textos, "estandar")

    assert len(resultado) == MAXIMO_FRAGMENTOS


def test_el_material_de_paciente_no_llega_a_cuentas_estandar():
    ids = [id_ for id_, _ in buscar_fragmentos("respiracion diafragmatica", TEXTOS, "estandar")]

    assert "M-01" not in ids


def test_el_mejor_fragmento_va_primero():
    textos = [
        {
            "id": "Q",
            "titulo": "x",
            "tema": "x",
            "modulo": "general",
            "modo": "estandar",
            "texto": "dormir bien por las noches",
        },
        {
            "id": "P",
            "titulo": "x",
            "tema": "x",
            "modulo": "general",
            "modo": "estandar",
            "texto": "dormir bien",
        },
    ]

    ids = [id_ for id_, _ in buscar_fragmentos("dormir bien", textos, "estandar")]

    assert ids == ["P", "Q"]


def test_la_consulta_no_distingue_tildes_ni_mayusculas():
    con = buscar_fragmentos("RESPIRACIÓN para el estrés", TEXTOS, "paciente")
    sin = buscar_fragmentos("respiracion para el estres", TEXTOS, "paciente")

    assert con == sin


def test_el_modulo_de_ansiedad_no_es_visible_fuera_de_modo_paciente():
    # Defensa en profundidad: la validación ya impide esta combinación.
    texto = {"modulo": "ansiedad", "modo": "estandar"}

    assert es_visible(texto, "estandar") is False
    assert es_visible(texto, "paciente") is True
