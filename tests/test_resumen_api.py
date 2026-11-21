"""POST /resumen y la vista del tratante con el último resumen (HU-17b)."""

import json
from datetime import datetime, timedelta

import pytest

from app.api.deps import obtener_resumidor
from app.main import app
from app.repositorios.mensajes import guardar_mensaje
from app.services import almacen as _almacen  # noqa: F401  (inicializa el almacén)
from app.services.almacen import ahora
from app.services.proveedor_llm import ProveedorNoDisponible
from tests.conftest import cabecera

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}


class ResumidorFalso:
    """Devuelve hechos fijos y guarda los mensajes que recibió."""

    def __init__(self, respuesta=None, error=None):
        self.respuesta = respuesta
        self.error = error
        self.recibidos = []

    def responder(self, mensaje, fragmentos):
        self.recibidos.append(mensaje)
        if self.error:
            raise self.error
        return self.respuesta


@pytest.fixture
def resumidor():
    falso = ResumidorFalso(respuesta=None)
    app.dependency_overrides[obtener_resumidor] = lambda: falso
    yield falso
    app.dependency_overrides.pop(obtener_resumidor, None)


def hoy_con(fecha_dia, texto="x"):
    return ahora() - timedelta(days=fecha_dia)


def conversar_con_luis(cliente, texto):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    cliente.post("/chat", json={"texto": texto}, headers=cabecera("luis"))


def sembrar_mensaje_de_luis(cliente, texto, hace_dias):
    with cliente.app.state.motor.begin() as conexion:
        guardar_mensaje(
            conexion,
            "luis",
            "usuario",
            "mensaje",
            texto,
            ahora() - timedelta(days=hace_dias),
        )


def resumen_con(hechos):
    return json.dumps({"hechos": hechos})


def test_el_tratante_genera_el_resumen_con_el_contrato(cliente, resumidor):
    fecha = ahora().date().isoformat()
    resumidor.respuesta = resumen_con([{"dia": fecha, "hecho": "Relató que durmió mal."}])
    conversar_con_luis(cliente, "dormí mal anoche")

    respuesta = cliente.post("/resumen", headers=cabecera("tratante"))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["paciente_id"] == "luis"
    assert cuerpo["generado_por_ia"] is True
    assert cuerpo["hechos"] == [{"fecha": fecha, "descripcion": "Relató que durmió mal."}]
    assert set(cuerpo) >= {
        "paciente_id",
        "desde",
        "hasta",
        "generado_en",
        "temas",
        "patrones",
        "alertas",
    }


def test_el_periodo_cubre_siete_dias_incluido_hoy(cliente, resumidor):
    respuesta = cliente.post("/resumen", headers=cabecera("tratante")).json()

    dias = (
        datetime.fromisoformat(respuesta["hasta"]) - datetime.fromisoformat(respuesta["desde"])
    ).days
    assert dias == 7


def test_solo_llegan_al_modelo_los_mensajes_de_la_ultima_semana(cliente, resumidor):
    sembrar_mensaje_de_luis(cliente, "mensaje antiguo", hace_dias=10)
    sembrar_mensaje_de_luis(cliente, "mensaje reciente", hace_dias=2)
    resumidor.respuesta = resumen_con([])

    cliente.post("/resumen", headers=cabecera("tratante"))

    assert len(resumidor.recibidos) == 1
    assert "mensaje reciente" in resumidor.recibidos[0]
    assert "mensaje antiguo" not in resumidor.recibidos[0]


def test_sin_mensajes_en_la_semana_no_se_llama_al_modelo(cliente, resumidor):
    respuesta = cliente.post("/resumen", headers=cabecera("tratante"))

    assert respuesta.status_code == 201
    assert respuesta.json()["hechos"] == []
    assert resumidor.recibidos == []


def test_solo_entran_las_alertas_del_periodo(cliente, resumidor):
    # Una alerta de hace diez días no debe aparecer en el resumen de esta semana.
    with cliente.app.state.motor.begin() as conexion:
        from app.repositorios.alertas import registrar_alerta

        registrar_alerta(conexion, "luis", "alto", "vieja", ahora() - timedelta(days=10))
        registrar_alerta(conexion, "luis", "alto", "reciente", ahora() - timedelta(days=1))

    cuerpo = cliente.post("/resumen", headers=cabecera("tratante")).json()

    assert [a["mensaje"] for a in cuerpo["alertas"]] == ["reciente"]


def test_el_paciente_no_puede_generar_el_resumen(cliente, resumidor):
    respuesta = cliente.post("/resumen", headers=cabecera("luis"))

    assert respuesta.status_code == 403
    assert resumidor.recibidos == []


def test_el_tratante_sin_vinculo_recibe_403(cliente, resumidor, monkeypatch):
    from app.api import deps

    monkeypatch.setitem(
        deps.CUENTAS_DEMO,
        "otro_tratante",
        {"nombre": "Otro", "rol": "tratante", "tratante_id": None},
    )

    respuesta = cliente.post("/resumen", headers=cabecera("otro_tratante"))

    assert respuesta.status_code == 403


def test_si_el_modelo_no_responde_no_se_guarda_nada(cliente, resumidor):
    sembrar_mensaje_de_luis(cliente, "hoy estoy bien", hace_dias=0)
    resumidor.error = ProveedorNoDisponible("no responde")

    respuesta = cliente.post("/resumen", headers=cabecera("tratante"))

    assert respuesta.status_code == 503
    assert cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()["resumen"] is None


def test_una_respuesta_del_modelo_mal_formada_da_502(cliente, resumidor):
    sembrar_mensaje_de_luis(cliente, "hoy estoy bien", hace_dias=1)
    resumidor.respuesta = "esto no es json"

    respuesta = cliente.post("/resumen", headers=cabecera("tratante"))

    assert respuesta.status_code == 502
    assert cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()["resumen"] is None


def test_la_vista_del_tratante_muestra_el_ultimo_resumen(cliente, resumidor):
    resumidor.respuesta = resumen_con([])
    cliente.post("/resumen", headers=cabecera("tratante"))
    sembrar_mensaje_de_luis(cliente, "hoy escribo de nuevo", hace_dias=0)
    resumidor.respuesta = resumen_con([{"dia": ahora().date().isoformat(), "hecho": "Segundo."}])
    segundo = cliente.post("/resumen", headers=cabecera("tratante")).json()

    vista = cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()

    assert vista["resumen"]["generado_en"] == segundo["generado_en"]
    assert vista["resumen"]["hechos"][0]["descripcion"] == "Segundo."


def test_el_resumen_sobrevive_al_reinicio(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool

    from app.api.deps import obtener_cola, obtener_expresiones
    from app.services.cola import ColaPendientes

    motor = create_engine(
        f"sqlite:///{tmp_path / 'holo.db'}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr("app.main.crear_motor", lambda: motor)
    app.dependency_overrides[obtener_expresiones] = lambda: ("expresion",)
    app.dependency_overrides[obtener_cola] = lambda: ColaPendientes(tmp_path / "c.jsonl")
    falso = ResumidorFalso(respuesta=resumen_con([]))
    app.dependency_overrides[obtener_resumidor] = lambda: falso
    try:
        with TestClient(app) as cliente:
            cliente.post("/resumen", headers=cabecera("tratante"))
        with TestClient(app) as cliente:
            vista = cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()
    finally:
        app.dependency_overrides.clear()
        motor.dispose()

    assert vista["resumen"] is not None
    assert vista["resumen"]["generado_por_ia"] is True
