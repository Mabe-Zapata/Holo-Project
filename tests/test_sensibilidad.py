"""Sensibilidad de la revisión de riesgo y del flujo del chat en todas las cuentas (HU-13, HU-21).

Las pruebas usan la lista real de expresiones, no la de prueba de conftest.py.
"""

import pytest

from app.api.deps import obtener_expresiones
from app.main import app
from app.services.almacen import CUENTAS_DEMO, almacen
from app.services.filtros import RESPUESTA_CLINICA, es_consulta_clinica
from app.services.riesgo import RUTA_TEXTO_CRISIS, cargar_expresiones, es_riesgo_alto
from tests.conftest import cabecera
from fastapi.testclient import TestClient

from pathlib import Path

EXPRESIONES_REALES = tuple(
    cargar_expresiones(str(RUTA_TEXTO_CRISIS.parent / "expresiones_riesgo.txt"))
)
CUENTAS = list(CUENTAS_DEMO)
# Solo las cuentas que conversan con la IA; el tratante recibe resúmenes, no chatea.
CUENTAS_CONVERSAN = ["ana", "luis"]
CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}

# Variantes de escritura de una misma expresión: mayúsculas, tildes, espacios y contexto.
VARIANTES_DE_RIESGO = [
    "quiero morir",
    "QUIERO   MORIR",
    "Hoy siento que ya no quiero seguir viviendo, de verdad.",
    "No le encuentro sentido a VIVIR últimamente.",
    "Estaría mejor muerta, lo pienso todos los días.",
    "A veces creo que nadie me extrañaría.",
    "Me quiero hacer daño cuando me siento así.",
]

HABITUALES = [
    "Hoy fue un buen día en la universidad.",
    "Estoy muy cansada después del examen.",
    "¿Cómo puedo respirar mejor cuando estoy nerviosa?",
    "Quiero hablar de mi relación con mi familia.",
    "Ayer salí a caminar con mi perra.",
    "¿Qué puedo hacer para dormir mejor?",
    "Gracias por escucharme.",
]

CLINICOS = [
    "¿Qué diagnóstico tengo según lo que te escribo?",
    "¿Cuántos miligramos debería tomar?",
    "¿Debo dejar de tomar mi medicación?",
    "Creo que tengo bipolaridad, ¿verdad?",
]


@pytest.fixture
def cliente_real():
    almacen.reiniciar()
    app.dependency_overrides[obtener_expresiones] = lambda: EXPRESIONES_REALES
    yield TestClient(app)
    app.dependency_overrides.clear()
    almacen.reiniciar()


def consentir(cliente, cuenta: str) -> None:
    r = cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera(cuenta))
    assert r.status_code == 201


# --- Sensibilidad de la detección (sin HTTP) ---------------------------------

@pytest.mark.parametrize("expresion", EXPRESIONES_REALES)
def test_cada_expresion_de_la_lista_se_detecta_en_cualquier_escritura(expresion):
    assert es_riesgo_alto(f"Mensaje: {expresion.upper()}", EXPRESIONES_REALES)


@pytest.mark.parametrize("texto", VARIANTES_DE_RIESGO)
def test_variantes_de_riesgo_se_detectan(texto):
    assert es_riesgo_alto(texto, EXPRESIONES_REALES)


@pytest.mark.parametrize("texto", HABITUALES)
def test_mensajes_habituales_no_activan_riesgo(texto):
    assert not es_riesgo_alto(texto, EXPRESIONES_REALES)


@pytest.mark.xfail(
    strict=True,
    reason="Límite conocido: la lista exige la expresión exacta; las paráfrasis se escapan.",
)
@pytest.mark.parametrize(
    "parafrasis",
    [
        "Quisiera no despertarme nunca más.",
        "Quiero dejar de existir.",
    ],
)
def test_parafrasis_de_riesgo(parafrasis):
    assert es_riesgo_alto(parafrasis, EXPRESIONES_REALES)


# --- Mismo comportamiento en todas las cuentas (HTTP) ------------------------

@pytest.mark.parametrize("cuenta", CUENTAS_CONVERSAN)
@pytest.mark.parametrize("texto", VARIANTES_DE_RIESGO)
def test_riesgo_muestra_crisis_en_todas_las_cuentas(cliente_real, cuenta, texto):
    consentir(cliente_real, cuenta)
    r = cliente_real.post("/chat", json={"texto": texto}, headers=cabecera(cuenta))
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["tipo"] == "crisis"
    assert cuerpo["riesgo"] == "alto"
    assert {rec["telefono"] for rec in cuerpo["recursos"]} == {"911", "171"}


@pytest.mark.parametrize("cuenta", CUENTAS_CONVERSAN)
@pytest.mark.parametrize("texto", HABITUALES)
def test_mensajes_habituales_no_muestran_crisis_en_ninguna_cuenta(cliente_real, cuenta, texto):
    consentir(cliente_real, cuenta)
    cuerpo = cliente_real.post("/chat", json={"texto": texto}, headers=cabecera(cuenta)).json()
    assert cuerpo["tipo"] == "respuesta"
    assert cuerpo["riesgo"] == "sin_riesgo"


@pytest.mark.parametrize("cuenta", CUENTAS)
def test_sin_consentimiento_ninguna_cuenta_conversa(cliente_real, cuenta):
    r = cliente_real.post("/chat", json={"texto": "hola"}, headers=cabecera(cuenta))
    assert r.status_code == 403


# --- Pendientes documentados (strict: al resolverse, la prueba debe quitarse) --

@pytest.mark.xfail(
    strict=True,
    reason="HU-08b pendiente: el filtro clínico aún no está conectado a POST /chat.",
)
@pytest.mark.parametrize("cuenta", CUENTAS_CONVERSAN)
@pytest.mark.parametrize("texto", CLINICOS)
def test_consulta_clinica_recibe_respuesta_fija_en_todas_las_cuentas(cliente_real, cuenta, texto):
    assert es_consulta_clinica(texto)
    consentir(cliente_real, cuenta)
    cuerpo = cliente_real.post("/chat", json={"texto": texto}, headers=cabecera(cuenta)).json()
    assert cuerpo["texto"] == RESPUESTA_CLINICA


def test_el_tratante_no_puede_conversar(cliente_real):
    consentir(cliente_real, "tratante")
    r = cliente_real.post("/chat", json={"texto": "hola"}, headers=cabecera("tratante"))
    assert r.status_code == 403
