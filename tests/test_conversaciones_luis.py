"""Conversaciones ficticias de Luis para el resumen semanal (BE-07a)."""

import json
import re
from collections import Counter
from pathlib import Path

from app.services.filtros import es_consulta_clinica
from app.services.riesgo import RUTA_TEXTO_CRISIS, cargar_expresiones, es_riesgo_alto

RUTA = Path(__file__).resolve().parents[1] / "data" / "conversaciones_luis.json"
DATOS = json.loads(RUTA.read_text(encoding="utf-8"))
MENSAJES = DATOS["mensajes"]
DE_LUIS = [m for m in MENSAJES if m["autor"] == "usuario"]
TIPOS_VALIDOS = {("usuario", "mensaje"), ("asistente", "respuesta"), ("asistente", "crisis")}
DIAS_DE_LA_SEMANA = re.compile(r"\b(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\b")


def test_cada_mensaje_esta_marcado_como_ficticio():
    assert all(m["ficticio"] is True for m in MENSAJES)


def test_siete_dias_con_al_menos_tres_mensajes_de_luis_por_dia():
    por_dia = Counter(m["dias_atras"] for m in DE_LUIS)
    assert sorted(por_dia) == list(range(1, 8))
    assert min(por_dia.values()) >= 3


def test_campos_validos_y_orden_cronologico():
    for m in MENSAJES:
        assert (m["autor"], m["tipo"]) in TIPOS_VALIDOS, m["id"]
        assert re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", m["hora"]), m["id"]
        assert m["texto"].strip(), m["id"]
    momentos = [(-m["dias_atras"], m["hora"]) for m in MENSAJES]
    assert momentos == sorted(momentos)


def test_ids_y_textos_unicos_para_cargar_sin_duplicar():
    assert len({m["id"] for m in MENSAJES}) == len(MENSAJES)
    assert len({m["texto"] for m in MENSAJES}) == len(MENSAJES)


def test_episodios_declarados_en_dias_con_mensajes():
    episodios = {e["tipo"]: e["dias_atras"] for e in DATOS["episodios"]}
    assert {"ansiedad", "sueño", "riesgo"} <= set(episodios)
    assert set(episodios.values()) <= {m["dias_atras"] for m in DE_LUIS}


def test_un_solo_mensaje_de_riesgo_seguido_de_la_respuesta_de_crisis():
    expresiones = cargar_expresiones(str(RUTA_TEXTO_CRISIS.parent / "expresiones_riesgo.txt"))
    riesgo = [
        i
        for i, m in enumerate(MENSAJES)
        if m["autor"] == "usuario" and es_riesgo_alto(m["texto"], expresiones)
    ]
    assert len(riesgo) == 1
    assert MENSAJES[riesgo[0] + 1]["tipo"] == "crisis"
    assert sum(m["tipo"] == "crisis" for m in MENSAJES) == 1
    episodio = next(e for e in DATOS["episodios"] if e["tipo"] == "riesgo")
    assert MENSAJES[riesgo[0]]["dias_atras"] == episodio["dias_atras"]


def test_sin_temas_clinicos_ni_dias_de_la_semana():
    # Las fechas son relativas al día de la carga: un día de la semana escrito no coincidiría.
    for m in MENSAJES:
        assert not es_consulta_clinica(m["texto"]), m["id"]
        assert not DIAS_DE_LA_SEMANA.search(m["texto"].lower()), m["id"]
