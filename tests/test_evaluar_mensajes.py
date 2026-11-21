import json
from pathlib import Path

import pytest

from app.services.riesgo import cargar_expresiones, es_riesgo_alto
from scripts.evaluar_mensajes import evaluar, resumen_markdown

RAIZ = Path(__file__).resolve().parent.parent
MENSAJES = json.loads((RAIZ / "tests" / "datos" / "mensajes_prueba.json").read_text("utf-8"))
EXPRESIONES = cargar_expresiones(str(RAIZ / "data" / "expresiones_riesgo.txt"))


def test_el_conjunto_tiene_al_menos_cuarenta_mensajes_de_cada_tipo():
    categorias = [m["categoria"] for m in MENSAJES]

    assert len(MENSAJES) >= 40
    assert categorias.count("riesgo") >= 10
    assert categorias.count("clinica") >= 10
    assert categorias.count("habitual") >= 10


def test_los_identificadores_son_unicos_y_cada_mensaje_tiene_texto():
    ids = [m["id"] for m in MENSAJES]

    assert len(ids) == len(set(ids))
    assert all(m["texto"].strip() for m in MENSAJES)


def test_marca_como_acierto_un_mensaje_de_riesgo_detectado():
    resultados = evaluar(
        [{"id": "X", "categoria": "riesgo", "texto": "quiero morir"}],
        expresiones=["quiero morir"],
    )

    assert resultados[0]["ok"] is True


def test_marca_como_fallo_un_mensaje_de_riesgo_no_detectado():
    resultados = evaluar(
        [{"id": "X", "categoria": "riesgo", "texto": "hoy estoy bien"}],
        expresiones=["quiero morir"],
    )

    assert resultados[0]["ok"] is False


def test_un_mensaje_habitual_no_debe_activar_ni_riesgo_ni_clinica():
    resultados = evaluar(
        [{"id": "X", "categoria": "habitual", "texto": "hoy cociné sopa"}],
        expresiones=["quiero morir"],
    )

    assert resultados[0]["ok"] is True
    assert resultados[0]["riesgo"] is False
    assert resultados[0]["clinica"] is False


def test_el_resumen_muestra_los_conteos_por_categoria():
    resultados = evaluar(
        [
            {"id": "A", "categoria": "riesgo", "texto": "quiero morir"},
            {"id": "B", "categoria": "riesgo", "texto": "hoy estoy bien"},
        ],
        expresiones=["quiero morir"],
    )

    resumen = resumen_markdown(resultados)

    assert "| riesgo | 2 | 1 | 1 |" in resumen
    assert "B" in resumen  # el fallo queda listado


def test_todos_los_mensajes_del_conjunto_se_evaluan_como_se_esperan():
    fallos = [r["id"] for r in evaluar(MENSAJES, EXPRESIONES) if not r["ok"]]

    assert fallos == []


@pytest.mark.parametrize(
    "texto",
    [
        "QUISE HACERME DAÑO",
        "quise hacerme dano",
        "¡Quise hacerme daño!",
        "  quisiera   hacerme   daño  ",
        "Anoche, en serio, quise matarme.",
    ],
)
def test_detecta_variantes_de_mayusculas_acentos_signos_y_espacios(texto):
    assert es_riesgo_alto(texto, EXPRESIONES)


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "   ",
        "Quise cortar el pasto esta mañana.",
        "Me muero de risa con ese chiste.",
        "No quiero seguir la dieta del gimnasio.",
    ],
)
def test_no_activa_riesgo_en_textos_vacios_o_cercanos(texto):
    assert not es_riesgo_alto(texto, EXPRESIONES)


def test_la_lista_no_tiene_expresiones_repetidas():
    assert len(EXPRESIONES) == len(set(EXPRESIONES))


def test_sin_lista_de_expresiones_nada_se_marca_como_riesgo():
    assert not es_riesgo_alto("quiero morir", [])
