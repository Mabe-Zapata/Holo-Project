"""Alertas de riesgo guardadas en la base y vistas por el tratante (HU-16)."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.api import deps
from app.api.deps import obtener_expresiones
from app.db import crear_tablas
from app.main import app
from app.repositorios.alertas import listar_alertas, registrar_alerta
from app.repositorios.usuarios import crear_cuentas_demo
from app.repositorios.vinculos import buscar_paciente_vinculado
from tests.conftest import EXPRESION_DE_PRUEBA, cabecera, crear_motor_pruebas

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}
INICIO = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def conexion():
    motor = crear_motor_pruebas()
    crear_tablas(motor)
    with motor.begin() as conexion_activa:
        crear_cuentas_demo(conexion_activa)
        yield conexion_activa
    motor.dispose()


def vista(cliente):
    return cliente.get("/tratante/paciente", headers=cabecera("tratante"))


def crisis(cliente, cuenta, texto=EXPRESION_DE_PRUEBA):
    return cliente.post("/chat", json={"texto": texto}, headers=cabecera(cuenta))


# --- Repositorio -----------------------------------------------------------


def test_listar_devuelve_las_alertas_en_orden_cronologico(conexion):
    registrar_alerta(conexion, "luis", "alto", "segunda", INICIO + timedelta(hours=1))
    registrar_alerta(conexion, "luis", "alto", "primera", INICIO)

    alertas = listar_alertas(conexion, "luis")

    assert [a["mensaje"] for a in alertas] == ["primera", "segunda"]
    assert all(a["nivel"] == "alto" for a in alertas)


def test_cada_paciente_solo_ve_sus_alertas(conexion):
    registrar_alerta(conexion, "luis", "alto", "de luis", INICIO)
    registrar_alerta(conexion, "ana", "alto", "de ana", INICIO)

    assert [a["mensaje"] for a in listar_alertas(conexion, "luis")] == ["de luis"]
    assert [a["mensaje"] for a in listar_alertas(conexion, "ana")] == ["de ana"]


def test_sin_alertas_devuelve_lista_vacia(conexion):
    assert listar_alertas(conexion, "luis") == []


def test_la_fecha_de_la_alerta_tiene_zona_horaria(conexion):
    registrar_alerta(conexion, "luis", "alto", "hola", INICIO)

    fecha = listar_alertas(conexion, "luis")[0]["fecha"]

    assert fecha.tzinfo is not None
    assert fecha == INICIO


def test_mensaje_largo_con_tildes_se_conserva_completo(conexion):
    texto = "á" * 1900 + " ¿estás bien? ñ"
    registrar_alerta(conexion, "luis", "alto", texto, INICIO)

    assert listar_alertas(conexion, "luis")[0]["mensaje"] == texto


@pytest.mark.parametrize("nivel", ["medio", "ALTO", "", None])
def test_nivel_desconocido_se_rechaza_sin_guardar(conexion, nivel):
    with pytest.raises(ValueError):
        registrar_alerta(conexion, "luis", nivel, "hola", INICIO)

    assert listar_alertas(conexion, "luis") == []


@pytest.mark.parametrize("mensaje", ["", "   ", "\n\t"])
def test_mensaje_vacio_se_rechaza_sin_guardar(conexion, mensaje):
    with pytest.raises(ValueError):
        registrar_alerta(conexion, "luis", "alto", mensaje, INICIO)

    assert listar_alertas(conexion, "luis") == []


def test_el_vinculo_activo_identifica_al_paciente_del_tratante(conexion):
    assert buscar_paciente_vinculado(conexion, "tratante") == "luis"


def test_quien_no_es_tratante_no_tiene_paciente_vinculado(conexion):
    assert buscar_paciente_vinculado(conexion, "luis") is None
    assert buscar_paciente_vinculado(conexion, "ana") is None


# --- API y ejecución en tiempo real ----------------------------------------


def test_frase_de_riesgo_registra_una_alerta_visible_para_el_tratante(cliente):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    respuesta = crisis(cliente, "luis")
    assert respuesta.json()["tipo"] == "crisis"

    cuerpo = vista(cliente).json()

    assert cuerpo["paciente_id"] == "luis"
    assert cuerpo["resumen"] is None
    assert len(cuerpo["alertas"]) == 1
    alerta = cuerpo["alertas"][0]
    assert alerta["nivel"] == "alto"
    assert alerta["mensaje"] == EXPRESION_DE_PRUEBA
    assert datetime.fromisoformat(alerta["fecha"]).tzinfo is not None


def test_mensaje_sin_riesgo_no_registra_alerta(cliente):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    cliente.post("/chat", json={"texto": "hoy dormí bien"}, headers=cabecera("luis"))

    assert vista(cliente).json()["alertas"] == []


def test_varias_crisis_quedan_todas_en_orden(cliente):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    for texto in [f"{EXPRESION_DE_PRUEBA} {n}" for n in range(3)]:
        crisis(cliente, "luis", texto)

    alertas = vista(cliente).json()["alertas"]

    assert [a["mensaje"] for a in alertas] == [f"{EXPRESION_DE_PRUEBA} {n}" for n in range(3)]
    fechas = [datetime.fromisoformat(a["fecha"]) for a in alertas]
    assert fechas == sorted(fechas)


def test_texto_de_2000_caracteres_con_riesgo_se_guarda_completo(cliente):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    texto = "a" * (2000 - len(EXPRESION_DE_PRUEBA) - 1) + " " + EXPRESION_DE_PRUEBA

    assert crisis(cliente, "luis", texto).status_code == 200

    assert vista(cliente).json()["alertas"][0]["mensaje"] == texto


def test_alerta_de_ana_no_aparece_en_la_vista_del_tratante(cliente):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("ana"))
    crisis(cliente, "ana")

    assert vista(cliente).json()["alertas"] == []


@pytest.mark.parametrize("cuenta", ["ana", "luis"])
def test_pacientes_no_pueden_consultar_la_vista_del_tratante(cliente, cuenta):
    respuesta = cliente.get("/tratante/paciente", headers=cabecera(cuenta))

    assert respuesta.status_code == 403


def test_tratante_sin_vinculo_recibe_403(cliente, monkeypatch):
    # Cuenta de tratante sin paciente: se agrega solo para esta prueba.
    monkeypatch.setitem(
        deps.CUENTAS_DEMO,
        "otro_tratante",
        {"nombre": "Otro tratante", "rol": "tratante", "tratante_id": None},
    )

    respuesta = cliente.get("/tratante/paciente", headers=cabecera("otro_tratante"))

    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == "No tienes un paciente vinculado."


def test_cuenta_desconocida_recibe_401_en_la_vista(cliente):
    respuesta = cliente.get("/tratante/paciente", headers=cabecera("nadie"))

    assert respuesta.status_code == 401


def test_la_alerta_sobrevive_al_reinicio_del_servidor(tmp_path, monkeypatch):
    motor = create_engine(
        f"sqlite:///{tmp_path / 'holo.db'}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr("app.main.crear_motor", lambda: motor)
    app.dependency_overrides[obtener_expresiones] = lambda: (EXPRESION_DE_PRUEBA,)
    try:
        with TestClient(app) as cliente:
            cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
            crisis(cliente, "luis")

        with TestClient(app) as cliente:
            alertas = vista(cliente).json()["alertas"]
    finally:
        app.dependency_overrides.clear()
        motor.dispose()

    assert [a["mensaje"] for a in alertas] == [EXPRESION_DE_PRUEBA]


def test_si_no_se_puede_registrar_la_alerta_la_crisis_no_se_confirma(cliente, monkeypatch):
    # Decisión: una crisis no se confirma si no quedó registrada (HU-16). El error sube
    # hasta el servidor, que responde 500 en producción; el cliente de pruebas lo relanza.
    def fallar(*args, **kwargs):
        raise RuntimeError("base no disponible")

    monkeypatch.setattr("app.api.routes.chat.registrar_alerta", fallar)
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))

    with pytest.raises(RuntimeError):
        crisis(cliente, "luis")

    monkeypatch.undo()
    assert vista(cliente).json()["alertas"] == []


def test_el_mensaje_del_usuario_queda_aunque_falle_la_alerta(cliente, monkeypatch):
    def fallar(*args, **kwargs):
        raise RuntimeError("base no disponible")

    monkeypatch.setattr("app.api.routes.chat.registrar_alerta", fallar)
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    with pytest.raises(RuntimeError):
        crisis(cliente, "luis")

    monkeypatch.undo()
    historial = cliente.get("/chat/historial", headers=cabecera("luis")).json()

    assert [m["autor"] for m in historial] == ["usuario"]
