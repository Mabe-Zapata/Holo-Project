import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from app.api.deps import obtener_expresiones
from app.main import app
from app.services.almacen import almacen

# Expresión ficticia para probar la ruta de crisis sin usar frases reales.
EXPRESION_DE_PRUEBA = "expresion de riesgo de prueba"


def crear_motor_pruebas():
    motor_pruebas = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Habilita las claves foráneas en SQLite.
    @event.listens_for(motor_pruebas, "connect")
    def activar_claves_foraneas(conexion, registro):
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return motor_pruebas


@pytest.fixture
def cliente(monkeypatch):
    almacen.reiniciar()
    motor_pruebas = crear_motor_pruebas()

    # La aplicación utilizará SQLite en lugar de PostgreSQL.
    monkeypatch.setattr("app.main.crear_motor", lambda: motor_pruebas)

    app.dependency_overrides[obtener_expresiones] = lambda: (EXPRESION_DE_PRUEBA,)

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        almacen.reiniciar()
        motor_pruebas.dispose()


def cabecera(usuario: str) -> dict:
    return {"X-Usuario-Id": usuario}
