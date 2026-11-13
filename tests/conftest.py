import pytest
from fastapi.testclient import TestClient

from app.api.deps import obtener_expresiones
from app.main import app
from app.services.almacen import almacen

# Expresión ficticia para probar la ruta de crisis sin usar frases reales.
EXPRESION_DE_PRUEBA = "expresion de riesgo de prueba"


@pytest.fixture
def cliente():
    almacen.reiniciar()
    app.dependency_overrides[obtener_expresiones] = lambda: (EXPRESION_DE_PRUEBA,)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    almacen.reiniciar()


def cabecera(usuario: str) -> dict:
    return {"X-Usuario-Id": usuario}
