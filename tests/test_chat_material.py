"""El chat responde a partir del material aprobado (HU-08b, HU-10, HU-12)."""

import pytest

from app.api.deps import obtener_proveedor
from app.api.routes.chat import RESPUESTA_SIN_MATERIAL
from app.core.config import obtener_configuracion
from app.main import app
from app.repositorios.material import guardar_texto
from app.services.filtros import RESPUESTA_CLINICA
from tests.conftest import EXPRESION_DE_PRUEBA, cabecera

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}


class ProveedorGrabador:
    """Registra cada llamada al modelo y los fragmentos que recibió."""

    def __init__(self):
        self.llamadas = []

    def responder(self, mensaje, fragmentos):
        self.llamadas.append((mensaje, list(fragmentos)))
        return "respuesta del modelo"


@pytest.fixture
def modelo():
    proveedor = ProveedorGrabador()
    app.dependency_overrides[obtener_proveedor] = lambda: proveedor
    yield proveedor
    app.dependency_overrides.pop(obtener_proveedor, None)


def agregar_material(cliente, **campos):
    base = {
        "id": "X-1",
        "titulo": "Material",
        "tema": "tema",
        "modulo": "general",
        "modo": "estandar",
        "estado": "aprobado",
        "fuente": "Fuente de prueba",
        "texto": "texto de prueba",
    }
    base.update(campos)
    with cliente.app.state.motor.begin() as conexion:
        guardar_texto(conexion, base)


def conversar(cliente, cuenta, texto):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera(cuenta))
    return cliente.post("/chat", json={"texto": texto}, headers=cabecera(cuenta)).json()


def test_sin_material_pertinente_responde_sin_llamar_al_modelo(cliente, modelo):
    cuerpo = conversar(cliente, "ana", "xilofono plutonio cuantico")

    assert cuerpo["texto"] == RESPUESTA_SIN_MATERIAL
    assert cuerpo["fragmentos"] == []
    assert modelo.llamadas == []


def test_con_material_el_modelo_recibe_los_fragmentos_y_la_respuesta_los_registra(cliente, modelo):
    cuerpo = conversar(cliente, "ana", "hola")

    assert cuerpo["texto"] == "respuesta del modelo"
    assert cuerpo["fragmentos"] == ["P-01"]
    assert len(modelo.llamadas) == 1
    _, fragmentos = modelo.llamadas[0]
    assert fragmentos == [
        ("P-01", "hola estresada dormir respirar conversacion mensaje pruebas material ayuda")
    ]


def test_una_consulta_clinica_recibe_la_respuesta_fija_sin_modelo(cliente, modelo):
    cuerpo = conversar(cliente, "ana", "¿Qué diagnóstico tengo según lo que te escribo?")

    assert cuerpo["texto"] == RESPUESTA_CLINICA
    assert modelo.llamadas == []


def test_una_crisis_no_consulta_el_material_ni_el_modelo(cliente, modelo):
    cuerpo = conversar(cliente, "luis", EXPRESION_DE_PRUEBA)

    assert cuerpo["tipo"] == "crisis"
    assert modelo.llamadas == []


def test_el_material_provisional_no_se_usa_por_defecto(cliente, modelo):
    agregar_material(cliente, id="PROV-1", estado="provisional", texto="girasol luna sombra")

    cuerpo = conversar(cliente, "ana", "girasol luna")

    assert cuerpo["texto"] == RESPUESTA_SIN_MATERIAL
    assert modelo.llamadas == []


def test_el_material_provisional_se_usa_si_la_configuracion_lo_permite(
    cliente, modelo, monkeypatch
):
    agregar_material(cliente, id="PROV-2", estado="provisional", texto="girasol luna sombra")
    monkeypatch.setenv("HOLO_ESTADOS_MATERIAL", "aprobado,provisional")
    obtener_configuracion.cache_clear()
    try:
        cuerpo = conversar(cliente, "ana", "girasol luna")
    finally:
        obtener_configuracion.cache_clear()

    assert cuerpo["fragmentos"] == ["PROV-2"]


def test_el_material_de_ansiedad_solo_llega_a_la_cuenta_paciente(cliente, modelo):
    agregar_material(
        cliente,
        id="ANS-1",
        modulo="ansiedad",
        modo="paciente",
        texto="respiracion diafragmatica calmada",
    )

    cuerpo_luis = conversar(cliente, "luis", "respiracion diafragmatica")
    cuerpo_ana = conversar(cliente, "ana", "respiracion diafragmatica")

    assert cuerpo_luis["fragmentos"] == ["ANS-1"]
    assert cuerpo_ana["texto"] == RESPUESTA_SIN_MATERIAL
