"""Prueba de extremo a extremo del flujo de la demostración (BE-17).

Recorre por HTTP, con modelos de prueba, la lista de riesgo que carga la aplicación y el material
de prueba de conftest.py: consentimiento, mensaje habitual respondido desde el material, mensaje
de riesgo, alerta visible para la tratante y resumen. Ana y Luis conversan en la misma base para
comprobar que nada de una cuenta llega a la otra. Solo mira lo que entra y sale de la API.
"""

import json
import re

import pytest

from app.api.deps import obtener_expresiones, obtener_proveedor, obtener_resumidor
from app.main import app
from app.services.proveedor_llm import ProveedorEco
from app.services.riesgo import TEXTO_CRISIS
from tests.conftest import cabecera

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}
ORDEN_DEL_HISTORIAL = [
    ("usuario", "mensaje"),
    ("asistente", "respuesta"),
    ("usuario", "mensaje"),
    ("asistente", "crisis"),
]
HECHO = "Relató que le cuesta dormir"
# Campos del contrato de odds/resumen.md.
CAMPOS_DEL_RESUMEN = {
    "paciente_id",
    "desde",
    "hasta",
    "generado_en",
    "generado_por_ia",
    "temas",
    "hechos",
    "patrones",
    "alertas",
}


def textos(cuenta: str) -> tuple[str, str]:
    """Mensaje habitual y mensaje de riesgo de la cuenta, con su nombre para distinguirlos.

    El habitual comparte palabras con el material de prueba. El de riesgo se arma con la lista
    que carga la aplicación, para no escribir una frase de riesgo en el código.
    """
    expresiones = obtener_expresiones()
    assert expresiones, "La lista de expresiones de riesgo que carga la aplicación está vacía."
    return (
        f"Hola, soy {cuenta} y necesito ayuda para dormir y respirar.",
        f"Soy {cuenta}. Hoy todo me pesa y {expresiones[0]}.",
    )


class ProveedorEspia(ProveedorEco):
    """Proveedor de prueba del chat que cuenta las veces que se le consulta."""

    llamadas = 0

    def responder(self, mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
        self.llamadas += 1
        return super().responder(mensaje, fragmentos)


class ResumidorFalso:
    """Responde como el modelo del resumen: un hecho por cada mensaje habitual que recibe.

    El resumen le entrega una línea "AAAA-MM-DD: texto" por cada mensaje del paciente.
    """

    def responder(self, mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
        encontrados = re.findall(r"(\d{4}-\d{2}-\d{2}): Hola, soy (\w+) y", mensaje)
        hechos = [{"dia": dia, "hecho": f"{HECHO} ({cuenta})."} for dia, cuenta in encontrados]
        return json.dumps({"hechos": hechos})


@pytest.fixture
def flujo(cliente):
    """El cliente de conftest, con los modelos de prueba y la lista de riesgo de la aplicación."""
    espia = ProveedorEspia()
    # Sin el reemplazo de conftest: la crisis depende de la lista que lee la aplicación.
    app.dependency_overrides.pop(obtener_expresiones, None)
    app.dependency_overrides[obtener_proveedor] = lambda: espia
    app.dependency_overrides[obtener_resumidor] = ResumidorFalso
    return cliente, espia  # `cliente` quita estos reemplazos al terminar


def conversar(cliente, espia, cuenta: str) -> None:
    """La cuenta acepta el consentimiento y envía su mensaje habitual y su mensaje de riesgo."""
    habitual, de_riesgo = textos(cuenta)
    quien = cabecera(cuenta)
    assert cliente.post("/chat", json={"texto": habitual}, headers=quien).status_code == 403
    assert cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=quien).status_code == 201
    llamadas = espia.llamadas

    respuesta = cliente.post("/chat", json={"texto": habitual}, headers=quien)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert (cuerpo["tipo"], cuerpo["riesgo"]) == ("respuesta", "sin_riesgo")
    # Responde el modelo a partir del material, y la respuesta registra lo que usó.
    assert cuerpo["fragmentos"] and cuerpo["texto"].strip()
    assert espia.llamadas == llamadas + 1

    respuesta = cliente.post("/chat", json={"texto": de_riesgo}, headers=quien)
    assert respuesta.status_code == 200
    crisis = respuesta.json()
    assert (crisis["tipo"], crisis["riesgo"], crisis["texto"]) == ("crisis", "alto", TEXTO_CRISIS)
    assert {recurso["telefono"] for recurso in crisis["recursos"]} == {"911", "171"}
    # Ante un riesgo responde el texto fijo: al modelo no se le consulta.
    assert espia.llamadas == llamadas + 1


def test_de_consentimiento_a_alerta_visible_solo_para_la_tratante(flujo):
    cliente, espia = flujo
    for cuenta in ("ana", "luis"):
        conversar(cliente, espia, cuenta)

    # Cada cuenta conserva solo su conversación, en orden.
    for cuenta in ("ana", "luis"):
        habitual, de_riesgo = textos(cuenta)
        historial = cliente.get("/chat/historial", headers=cabecera(cuenta))
        assert historial.status_code == 200
        mensajes = historial.json()
        assert [(m["autor"], m["tipo"]) for m in mensajes] == ORDEN_DEL_HISTORIAL
        assert [mensajes[i]["texto"] for i in (0, 2, 3)] == [habitual, de_riesgo, TEXTO_CRISIS]

    # La tratante ve solo la alerta de su paciente, con el mensaje que la originó, y no la
    # conversación.
    habitual, de_riesgo = textos("luis")
    vista = cliente.get("/tratante/paciente", headers=cabecera("tratante"))
    assert vista.status_code == 200
    assert vista.json()["paciente_id"] == "luis"
    assert [(a["nivel"], a["mensaje"]) for a in vista.json()["alertas"]] == [("alto", de_riesgo)]
    assert habitual not in vista.text

    # Nadie más accede a lo que no le corresponde.
    assert cliente.get("/chat/historial", headers=cabecera("tratante")).status_code == 403
    for cuenta in ("ana", "luis"):
        assert cliente.get("/tratante/paciente", headers=cabecera(cuenta)).status_code == 403
        assert cliente.post("/resumen", headers=cabecera(cuenta)).status_code == 403


def test_la_tratante_recibe_el_resumen_de_su_paciente(flujo):
    cliente, espia = flujo
    for cuenta in ("ana", "luis"):
        conversar(cliente, espia, cuenta)
    habitual, de_riesgo = textos("luis")
    dia = cliente.get("/chat/historial", headers=cabecera("luis")).json()[0]["fecha"][:10]
    tratante = cabecera("tratante")

    resumen = cliente.post("/resumen", headers=tratante)
    assert resumen.status_code == 201
    cuerpo = resumen.json()
    assert CAMPOS_DEL_RESUMEN <= cuerpo.keys()
    assert (cuerpo["paciente_id"], cuerpo["generado_por_ia"]) == ("luis", True)
    # El modelo recibió el mensaje habitual de Luis, con su día, y nada de Ana.
    assert cuerpo["hechos"] == [{"fecha": dia, "descripcion": f"{HECHO} (luis)."}]
    assert [(a["nivel"], a["mensaje"]) for a in cuerpo["alertas"]] == [("alto", de_riesgo)]
    assert habitual not in resumen.text  # el resumen no copia la conversación (RN-06)

    # La vista de la tratante muestra ese mismo resumen.
    guardado = cliente.get("/tratante/paciente", headers=tratante).json()["resumen"]
    assert (guardado["generado_en"], guardado["hechos"]) == (
        cuerpo["generado_en"],
        cuerpo["hechos"],
    )
