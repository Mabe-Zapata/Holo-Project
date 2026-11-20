import json

import pytest

from app.services.prompts import cargar_prompt_sistema
from app.services.proveedor_llm import (
    ProveedorCompatibleOpenAI,
    ProveedorDiferido,
    ProveedorEco,
    ProveedorNoDisponible,
    crear_proveedor,
)
from tests.conftest import cabecera

PROMPT = cargar_prompt_sistema().texto


class TransporteFalso:
    """Registra la petición y devuelve la respuesta preparada (sin red)."""

    def __init__(self, respuesta=None, error=None):
        self.respuesta = respuesta
        self.error = error
        self.enviado = None

    def __call__(self, url, cabeceras, cuerpo, timeout):
        self.enviado = {"url": url, "cabeceras": cabeceras, "cuerpo": json.loads(cuerpo)}
        if self.error:
            raise self.error
        return self.respuesta


def respuesta_de_chat(texto: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": texto}}]}


def proveedor(transporte) -> ProveedorCompatibleOpenAI:
    return ProveedorCompatibleOpenAI(
        url_base="https://api.ejemplo.test/v1",
        api_key="clave-de-prueba",
        modelo="modelo-de-prueba",
        prompt=PROMPT,
        transporte=transporte,
    )


def test_eco_no_cambia_su_comportamiento():
    assert ProveedorEco().responder("hola", []) == "[eco] hola"


def test_envia_el_prompt_del_sistema_como_primer_mensaje():
    falso = TransporteFalso(respuesta_de_chat("Te escucho."))
    proveedor(falso).responder("Estoy cansada", [("m-01", "Respira despacio.")])
    mensajes = falso.enviado["cuerpo"]["messages"]
    assert mensajes[0] == {"role": "system", "content": PROMPT}


def test_la_entrada_del_usuario_va_entre_etiquetas_y_con_el_material():
    falso = TransporteFalso(respuesta_de_chat("Te escucho."))
    proveedor(falso).responder("Estoy cansada", [("m-01", "Respira despacio.")])
    usuario = falso.enviado["cuerpo"]["messages"][1]["content"]
    assert "<mensaje>\nEstoy cansada\n</mensaje>" in usuario
    assert "[m-01] Respira despacio." in usuario


def test_devuelve_el_texto_de_la_respuesta():
    falso = TransporteFalso(respuesta_de_chat("  Te escucho.  "))
    assert proveedor(falso).responder("hola", []) == "Te escucho."


def test_usa_el_modelo_y_la_clave_configurados():
    falso = TransporteFalso(respuesta_de_chat("ok"))
    proveedor(falso).responder("hola", [])
    assert falso.enviado["cuerpo"]["model"] == "modelo-de-prueba"
    assert falso.enviado["cabeceras"]["Authorization"] == "Bearer clave-de-prueba"
    assert falso.enviado["url"] == "https://api.ejemplo.test/v1/chat/completions"


def test_error_del_servicio_se_convierte_en_no_disponible():
    with pytest.raises(ProveedorNoDisponible):
        proveedor(TransporteFalso(error=OSError("sin red"))).responder("hola", [])


@pytest.mark.parametrize("respuesta", [{}, {"choices": []}, {"choices": [{"message": {}}]}])
def test_respuesta_mal_formada_se_convierte_en_no_disponible(respuesta):
    with pytest.raises(ProveedorNoDisponible):
        proveedor(TransporteFalso(respuesta=respuesta)).responder("hola", [])


def test_crear_proveedor_eco_por_defecto():
    assert isinstance(crear_proveedor("eco"), ProveedorEco)


def test_crear_proveedor_real_exige_clave_y_modelo():
    with pytest.raises(ValueError):
        crear_proveedor("groq", clave="", modelo="m", url_base="https://x.test/v1", prompt=PROMPT)
    with pytest.raises(ValueError):
        crear_proveedor("groq", clave="k", modelo="", url_base="https://x.test/v1", prompt=PROMPT)


def test_crear_proveedor_real_con_configuracion_completa():
    p = crear_proveedor("groq", clave="k", modelo="m", url_base="https://x.test/v1", prompt=PROMPT)
    assert isinstance(p, ProveedorCompatibleOpenAI)


def test_proveedor_desconocido_falla_al_arrancar():
    with pytest.raises(ValueError):
        crear_proveedor("inexistente", clave="", modelo="", url_base="", prompt=PROMPT)


class ProveedorCaido:
    def responder(self, mensaje, fragmentos):
        raise ProveedorNoDisponible("detalle técnico que no debe salir")


def test_si_el_modelo_no_responde_la_ruta_da_503_sin_detalle(cliente):
    from app.api.deps import obtener_proveedor
    from app.main import app

    app.dependency_overrides[obtener_proveedor] = lambda: ProveedorCaido()
    cliente.post(
        "/consentimiento",
        json={"mayor_de_edad": True, "acepta": True},
        headers={"X-Usuario-Id": "ana"},
    )
    r = cliente.post("/chat", json={"texto": "hola"}, headers={"X-Usuario-Id": "ana"})
    assert r.status_code == 503
    assert "detalle técnico" not in r.text


@pytest.mark.parametrize("contenido", [None, "   ", {"unexpected": "object"}, []])
def test_contenido_invalido_del_proveedor_devuelve_503(cliente, contenido):
    from app.api.deps import obtener_proveedor
    from app.main import app

    falso = TransporteFalso(respuesta_de_chat(contenido))
    app.dependency_overrides[obtener_proveedor] = lambda: proveedor(falso)
    headers = {"X-Usuario-Id": "ana"}
    cliente.post("/consentimiento", json={"mayor_de_edad": True, "acepta": True}, headers=headers)
    respuesta = cliente.post("/chat", json={"texto": "hola"}, headers=headers)
    assert respuesta.status_code == 503
    assert respuesta.json()["detail"] == "El asistente no está disponible en este momento."
    historial = cliente.get("/chat/historial", headers=headers).json()
    assert [m["autor"] for m in historial] == ["usuario"]


@pytest.fixture
def proveedor_sin_configuracion(monkeypatch):
    from app.api import deps
    from app.core.config import Configuracion

    cfg = Configuracion(_env_file=None, proveedor_llm="groq", llm_api_key="", llm_modelo="")
    monkeypatch.setattr(deps, "obtener_configuracion", lambda: cfg)
    deps.obtener_proveedor.cache_clear()
    yield
    deps.obtener_proveedor.cache_clear()


def test_crisis_no_construye_el_proveedor_real(cliente, proveedor_sin_configuracion, monkeypatch):
    from app.api import deps
    from tests.conftest import EXPRESION_DE_PRUEBA

    def no_crear(*args, **kwargs):
        pytest.fail("Una crisis no debe construir el proveedor real")

    monkeypatch.setattr(deps, "crear_proveedor", no_crear)
    headers = {"X-Usuario-Id": "luis"}
    cliente.post("/consentimiento", json={"mayor_de_edad": True, "acepta": True}, headers=headers)
    respuesta = cliente.post("/chat", json={"texto": EXPRESION_DE_PRUEBA}, headers=headers)
    assert respuesta.status_code == 200
    assert respuesta.json()["tipo"] == "crisis"
    vista = cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()
    assert len(vista["alertas"]) == 1
    historial = cliente.get("/chat/historial", headers=headers).json()
    assert [m["autor"] for m in historial] == ["usuario", "asistente"]


def test_configuracion_incompleta_devuelve_503_generico(cliente, proveedor_sin_configuracion):
    headers = {"X-Usuario-Id": "ana"}
    cliente.post("/consentimiento", json={"mayor_de_edad": True, "acepta": True}, headers=headers)
    respuesta = cliente.post("/chat", json={"texto": "hola"}, headers=headers)
    assert respuesta.status_code == 503
    assert respuesta.json()["detail"] == "El asistente no está disponible en este momento."
    assert "HOLO_LLM" not in respuesta.text


def test_configuracion_incompleta_no_impide_rechazar_sin_consentimiento(
    cliente, proveedor_sin_configuracion
):
    respuesta = cliente.post("/chat", json={"texto": "hola"}, headers={"X-Usuario-Id": "ana"})
    assert respuesta.status_code == 403
    assert cliente.get("/chat/historial", headers={"X-Usuario-Id": "ana"}).json() == []


@pytest.mark.parametrize("usuario, texto, codigo", [("tratante", "hola", 403), ("ana", None, 422)])
def test_rol_y_validacion_preceden_al_proveedor_sin_configurar(
    cliente, proveedor_sin_configuracion, monkeypatch, usuario, texto, codigo
):
    from app.api import deps

    def no_crear(*args, **kwargs):
        pytest.fail("Un rechazo de entrada o permiso no debe construir el proveedor")

    monkeypatch.setattr(deps, "crear_proveedor", no_crear)
    headers = {"X-Usuario-Id": usuario}
    cliente.post("/consentimiento", json={"mayor_de_edad": True, "acepta": True}, headers=headers)
    respuesta = cliente.post("/chat", json={"texto": texto}, headers=headers)
    assert respuesta.status_code == codigo
    assert cliente.get("/chat/historial", headers={"X-Usuario-Id": "ana"}).json() == []
    vista = cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()
    assert vista["alertas"] == []


def test_proveedor_diferido_no_comparte_instancias_entre_respuestas():
    instancias = []

    def fabrica():
        instancia = ProveedorEco()
        instancias.append(instancia)
        return instancia

    diferido = ProveedorDiferido(fabrica)
    assert diferido.responder("primero", []) == "[eco] primero"
    assert diferido.responder("segundo", []) == "[eco] segundo"
    assert len(instancias) == 2
    assert instancias[0] is not instancias[1]
