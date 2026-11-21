"""Conversación de chat conectada a la base (BE-04, HU-06): reinicio y aislamiento."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import obtener_expresiones
from app.main import app
from tests.conftest import EXPRESION_DE_PRUEBA, cabecera

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}


def test_la_conversacion_sobrevive_al_reinicio_del_servidor(tmp_path, monkeypatch):
    # Un archivo de SQLite simula la base de datos que sigue viva tras reiniciar la API.
    motor = create_engine(
        f"sqlite:///{tmp_path / 'holo.db'}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr("app.main.crear_motor", lambda: motor)
    app.dependency_overrides[obtener_expresiones] = lambda: (EXPRESION_DE_PRUEBA,)
    try:
        with TestClient(app) as cliente:
            cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("ana"))
            cliente.post("/chat", json={"texto": "Estoy estresada"}, headers=cabecera("ana"))

        with TestClient(app) as cliente:
            historial = cliente.get("/chat/historial", headers=cabecera("ana")).json()
    finally:
        app.dependency_overrides.clear()
        motor.dispose()

    assert [m["autor"] for m in historial] == ["usuario", "asistente"]
    assert historial[0]["texto"] == "Estoy estresada"


def test_cada_paciente_solo_ve_su_propia_conversacion(cliente):
    for cuenta, texto in [("ana", "mensaje de ana"), ("luis", "mensaje de luis")]:
        cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera(cuenta))
        cliente.post("/chat", json={"texto": texto}, headers=cabecera(cuenta))

    historial = cliente.get("/chat/historial", headers=cabecera("luis")).json()

    assert len(historial) == 2
    assert all("mensaje de ana" not in m["texto"] for m in historial)
    assert historial[0]["texto"] == "mensaje de luis"
