"""Crisis y mensajes cuando la base falla o se recupera (HU-16, cola local).

Simulan una base caída con un motor que falla al abrir cada conexión: es el fallo real
en producción, porque la consulta de consentimiento ocurre antes de cualquier escritura.
"""

import json
import threading
import time
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import OperationalError

from app.api.deps import obtener_motor, obtener_proveedor
from app.main import app
from app.repositorios.alertas import listar_alertas
from app.services.cola import ColaPendientes
from app.services.sincronizador import Sincronizador, sincronizar
from tests.conftest import EXPRESION_DE_PRUEBA, cabecera

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}
FECHA = "2026-11-19T12:00:00+00:00"


class MotorCaido:
    """Imita una base inalcanzable: cualquier conexión falla."""

    def _caer(self):
        raise OperationalError("conectar", {}, Exception("base no disponible"))

    def connect(self):
        self._caer()

    def begin(self):
        self._caer()


class ProveedorContador:
    def __init__(self):
        self.llamadas = 0

    def responder(self, texto, fragmentos):
        self.llamadas += 1
        return f"respuesta {self.llamadas}"


def caer_base():
    app.dependency_overrides[obtener_motor] = lambda: MotorCaido()


def reponer_base():
    app.dependency_overrides.pop(obtener_motor, None)


@pytest.fixture
def base_caida():
    caer_base()
    yield
    reponer_base()


@pytest.fixture(autouse=True)
def base_siempre_disponible_al_terminar():
    yield
    reponer_base()


@pytest.fixture
def proveedor_contador():
    proveedor = ProveedorContador()
    app.dependency_overrides[obtener_proveedor] = lambda: proveedor
    yield proveedor
    app.dependency_overrides.pop(obtener_proveedor, None)


def cola_del_cliente(tmp_path):
    return ColaPendientes(tmp_path / "cola.jsonl")


def crisis(cliente, cuenta="luis", texto=EXPRESION_DE_PRUEBA, id_evento=None):
    cuerpo = {"texto": texto}
    if id_evento is not None:
        cuerpo["id_evento"] = id_evento
    return cliente.post("/chat", json=cuerpo, headers=cabecera(cuenta))


def vista(cliente):
    return cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()


# --- Crisis con la base caída -------------------------------------------------


def test_crisis_responde_ayuda_aunque_la_base_este_caida(cliente, tmp_path):
    respuesta = crisis(cliente, id_evento="evento-caida-1")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["tipo"] == "crisis"
    assert cuerpo["riesgo"] == "alto"
    assert [r["telefono"] for r in cuerpo["recursos"]] == ["911", "171"]


def test_la_crisis_con_base_caida_queda_en_la_cola_local(cliente, tmp_path, base_caida):
    crisis(cliente, id_evento="evento-caida-2")

    pendientes = cola_del_cliente(tmp_path).pendientes()

    assert len(pendientes) == 1
    assert pendientes[0]["id_evento"] == "evento-caida-2"
    assert pendientes[0]["usuario_id"] == "luis"
    assert pendientes[0]["texto"] == EXPRESION_DE_PRUEBA
    assert pendientes[0]["fecha"].endswith("+00:00")


def test_el_tratante_ve_cuantas_alertas_estan_en_sincronizacion(cliente, tmp_path, base_caida):
    crisis(cliente, id_evento="evento-caida-3")
    reponer_base()  # la base vuelve

    cuerpo = vista(cliente)

    assert cuerpo["alertas"] == []
    assert cuerpo["alertas_pendientes"] == 1


def test_un_mensaje_normal_con_base_caida_falla_sin_perder_nada(cliente, tmp_path, base_caida):
    # El envío normal sí requiere la base (consentimiento e historial). El cliente reintenta.
    with pytest.raises(OperationalError):
        cliente.post("/chat", json={"texto": "hoy dormí bien"}, headers=cabecera("luis"))

    assert cola_del_cliente(tmp_path).pendientes() == []


def test_sincronizar_con_la_base_caida_conserva_los_eventos(cliente, tmp_path, base_caida):
    crisis(cliente, id_evento="evento-caida-4")

    resueltos = sincronizar(MotorCaido(), cola_del_cliente(tmp_path))

    assert resueltos == 0
    assert len(cola_del_cliente(tmp_path).pendientes()) == 1


# --- Sincronización al recuperarse la base ------------------------------------


def test_al_volver_la_base_el_evento_pendiente_pasa_a_las_alertas(cliente, tmp_path):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    caer_base()
    crisis(cliente, id_evento="evento-vuelve-1")
    reponer_base()
    cola = cola_del_cliente(tmp_path)

    resueltos = sincronizar(app.state.motor, cola)

    assert resueltos == 1
    assert cola.pendientes() == []
    alertas = vista(cliente)["alertas"]
    assert [a["mensaje"] for a in alertas] == [EXPRESION_DE_PRUEBA]
    historial = cliente.get("/chat/historial", headers=cabecera("luis")).json()
    assert [m["autor"] for m in historial] == ["usuario", "asistente"]
    assert historial[1]["tipo"] == "crisis"


def test_reenviar_el_mismo_evento_con_la_base_viva_no_duplica(cliente, tmp_path):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))

    assert crisis(cliente, id_evento="evento-doble").status_code == 200
    assert crisis(cliente, id_evento="evento-doble").status_code == 200

    assert len(vista(cliente)["alertas"]) == 1
    historial = cliente.get("/chat/historial", headers=cabecera("luis")).json()
    assert [m["autor"] for m in historial] == ["usuario", "asistente"]
    # Con la base viva un reintento no debe pasar por la cola.
    assert cola_del_cliente(tmp_path).pendientes() == []


def test_reenvio_online_de_un_evento_en_cola_no_duplica_al_sincronizar(cliente, tmp_path):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    caer_base()
    crisis(cliente, id_evento="evento-cola-y-online")
    reponer_base()

    # El cliente reenvía el mismo mensaje mientras el evento sigue en la cola.
    assert crisis(cliente, id_evento="evento-cola-y-online").status_code == 200
    sincronizar(app.state.motor, cola_del_cliente(tmp_path))

    assert len(vista(cliente)["alertas"]) == 1
    assert cola_del_cliente(tmp_path).pendientes() == []


def test_sincronizar_dos_veces_no_duplica(cliente, tmp_path):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    caer_base()
    crisis(cliente, id_evento="evento-dos-veces")
    reponer_base()
    cola = cola_del_cliente(tmp_path)
    evento = cola.pendientes()[0]

    sincronizar(app.state.motor, cola)
    cola.encolar(evento)  # simula un fallo al quitar la línea después de guardar
    sincronizar(app.state.motor, cola)

    with app.state.motor.connect() as conexion:
        assert len(listar_alertas(conexion, "luis")) == 1


# --- Consentimiento ------------------------------------------------------------


def test_crisis_sin_consentimiento_responde_ayuda_y_no_guarda_nada(cliente, tmp_path):
    respuesta = crisis(cliente, id_evento="evento-sin-consent")

    assert respuesta.json()["tipo"] == "crisis"
    assert vista(cliente)["alertas"] == []
    assert cola_del_cliente(tmp_path).pendientes() == []


def test_evento_en_cola_sin_consentimiento_se_descarta_al_sincronizar(
    cliente, tmp_path, base_caida
):
    crisis(cliente, id_evento="evento-sin-consent-cola")
    reponer_base()
    cola = cola_del_cliente(tmp_path)

    resueltos = sincronizar(app.state.motor, cola)

    assert resueltos == 1
    assert cola.pendientes() == []
    assert vista(cliente)["alertas"] == []


# --- Cola local ----------------------------------------------------------------


def test_la_cola_sobrevive_a_reabrirla(tmp_path):
    ColaPendientes(tmp_path / "c.jsonl").encolar({"id_evento": "a1", "usuario_id": "luis"})

    pendientes = ColaPendientes(tmp_path / "c.jsonl").pendientes()

    assert [e["id_evento"] for e in pendientes] == ["a1"]


def test_quitar_solo_retira_el_evento_indicado(tmp_path):
    cola = ColaPendientes(tmp_path / "c.jsonl")
    cola.encolar({"id_evento": "uno-uno", "usuario_id": "luis"})
    cola.encolar({"id_evento": "dos-dos", "usuario_id": "luis"})

    cola.quitar("uno-uno")

    assert [e["id_evento"] for e in cola.pendientes()] == ["dos-dos"]


def test_una_linea_danada_se_omite_y_no_impide_las_demas(tmp_path):
    archivo = tmp_path / "c.jsonl"
    archivo.write_text(
        '{"id_evento": "bueno-1", "usuario_id": "luis"}\n'
        '{"id_evento": "roto", "usuario_id"\n'
        "\n"
        '{"sin_id": true}\n'
        '{"id_evento": "bueno-2", "usuario_id": "luis"}\n',
        encoding="utf-8",
    )

    ids = [e["id_evento"] for e in ColaPendientes(archivo).pendientes()]

    assert ids == ["bueno-1", "bueno-2"]


def test_sincronizar_salta_un_evento_malformado_y_aplica_el_resto(cliente, tmp_path):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    cola = cola_del_cliente(tmp_path)
    cola.encolar({"id_evento": "malformado-1", "usuario_id": "luis"})  # sin texto ni fecha
    cola.encolar(
        {
            "id_evento": "valido-1",
            "usuario_id": "luis",
            "texto": EXPRESION_DE_PRUEBA,
            "fecha": FECHA,
        }
    )

    resueltos = sincronizar(app.state.motor, cola)

    assert resueltos == 1
    assert [e["id_evento"] for e in cola.pendientes()] == ["malformado-1"]
    assert len(vista(cliente)["alertas"]) == 1


def test_encolar_desde_varios_hilos_no_pierde_eventos(tmp_path):
    cola = ColaPendientes(tmp_path / "c.jsonl")

    hilos = [
        threading.Thread(
            target=cola.encolar, args=({"id_evento": f"h-{n:03d}", "usuario_id": "luis"},)
        )
        for n in range(30)
    ]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert len(cola.pendientes()) == 30


def test_la_linea_guardada_es_json_con_texto_en_utf8(tmp_path):
    cola = ColaPendientes(tmp_path / "c.jsonl")
    cola.encolar({"id_evento": "tilde-1", "usuario_id": "luis", "texto": "¿estás bien? ñ"})

    linea = (tmp_path / "c.jsonl").read_text(encoding="utf-8").strip()

    assert json.loads(linea)["texto"] == "¿estás bien? ñ"


# --- Entrada y reintentos ------------------------------------------------------


@pytest.mark.parametrize("id_malo", ["corto", "con espacios aquí", "x" * 65, "ñandú-id-1"])
def test_id_de_evento_con_formato_invalido_se_rechaza(cliente, id_malo):
    respuesta = cliente.post(
        "/chat", json={"texto": "hola", "id_evento": id_malo}, headers=cabecera("luis")
    )

    assert respuesta.status_code == 422


def test_reintento_normal_devuelve_la_misma_respuesta_sin_llamar_al_modelo(
    cliente, proveedor_contador
):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("ana"))
    primera = cliente.post(
        "/chat", json={"texto": "hola", "id_evento": "reintento-001"}, headers=cabecera("ana")
    ).json()
    segunda = cliente.post(
        "/chat", json={"texto": "hola", "id_evento": "reintento-001"}, headers=cabecera("ana")
    ).json()

    assert primera == segunda
    assert proveedor_contador.llamadas == 1
    historial = cliente.get("/chat/historial", headers=cabecera("ana")).json()
    assert [m["autor"] for m in historial] == ["usuario", "asistente"]


def test_mensaje_sin_id_recibe_uno_propio_y_no_se_confunde_con_otro(cliente, proveedor_contador):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("ana"))

    cliente.post("/chat", json={"texto": "hola"}, headers=cabecera("ana"))
    cliente.post("/chat", json={"texto": "hola"}, headers=cabecera("ana"))

    assert proveedor_contador.llamadas == 2


# --- Bucle de sincronización en segundo plano -----------------------------------


def test_el_sincronizador_en_segundo_plano_aplica_eventos_y_se_detiene(cliente, tmp_path):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    caer_base()
    crisis(cliente, id_evento="evento-hilo-1")
    reponer_base()
    sincronizador = Sincronizador(app.state.motor, cola_del_cliente(tmp_path), 0.05)

    sincronizador.iniciar()
    try:
        limite = time.monotonic() + 5
        while time.monotonic() < limite and len(vista(cliente)["alertas"]) < 1:
            time.sleep(0.05)
    finally:
        sincronizador.detener()

    assert len(vista(cliente)["alertas"]) == 1
    assert cola_del_cliente(tmp_path).pendientes() == []


def test_fecha_de_la_cola_es_aware_y_se_respeta_al_sincronizar(cliente, tmp_path, base_caida):
    crisis(cliente, id_evento="evento-fecha")
    reponer_base()
    evento = cola_del_cliente(tmp_path).pendientes()[0]

    fecha = datetime.fromisoformat(evento["fecha"])

    assert fecha.tzinfo is not None
    assert fecha.astimezone(timezone.utc).tzinfo is not None
