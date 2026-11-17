"""Los registros nunca contienen el texto de los mensajes (BE-15)."""

import io
import logging
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.config import obtener_configuracion
from app.core.logging import configurar_registros
from app.db import crear_motor, crear_tablas, mensajes
from app.main import crear_app
from tests.conftest import EXPRESION_DE_PRUEBA, cabecera

TEXTO = "Mensaje privado de prueba 7f3a"


@pytest.fixture(autouse=True)
def restaurar_niveles():
    raiz, propio = logging.getLogger(), logging.getLogger("app")
    niveles = raiz.level, propio.level
    yield
    raiz.setLevel(niveles[0])
    propio.setLevel(niveles[1])


def test_el_nivel_se_toma_de_la_variable_de_entorno(monkeypatch):
    monkeypatch.setenv("HOLO_NIVEL_REGISTROS", "ERROR")
    obtener_configuracion.cache_clear()
    try:
        crear_app()
        assert logging.getLogger("app").level == logging.ERROR
    finally:
        obtener_configuracion.cache_clear()


def test_las_bibliotecas_no_registran_por_debajo_de_warning(caplog):
    configurar_registros("DEBUG")
    # Simula una biblioteca que en DEBUG escribe lo que envía, como el prompt al modelo.
    logging.getLogger("httpx").debug(TEXTO)
    logging.getLogger("app.prueba").debug("registro propio visible")
    assert "registro propio visible" in caplog.text
    assert TEXTO not in caplog.text


def test_un_error_de_la_base_no_muestra_el_texto():
    motor = crear_motor("sqlite:///:memory:")
    crear_tablas(motor)
    fila = {
        "usuario_id": None,  # viola NOT NULL para provocar el error
        "autor": "usuario",
        "tipo": "mensaje",
        "texto": TEXTO,
        "creado_en": datetime.now(timezone.utc),
    }
    with pytest.raises(IntegrityError) as error, motor.begin() as conexion:
        conexion.execute(mensajes.insert(), fila)
    assert TEXTO not in str(error.value)


def test_las_trazas_de_excepciones_ocultan_el_detalle():
    # Como uvicorn: un manejador propio que no propaga, creado antes de configurar los registros.
    salida = io.StringIO()
    servidor = logging.getLogger("prueba.servidor")
    servidor.propagate = False
    servidor.addHandler(logging.StreamHandler(salida))
    configurar_registros("INFO")
    detalle = f"no se pudo insertar\nDETAIL:  Failing row contains (luis, {TEXTO})"
    try:
        try:
            raise ValueError(detalle)  # imita el error de PostgreSQL con la fila
        except ValueError as error:
            raise RuntimeError("fallo al guardar el mensaje") from error
    except RuntimeError:
        servidor.exception("Exception in ASGI application")
    servidor.handlers.clear()
    registrado = salida.getvalue()
    assert "RuntimeError: fallo al guardar el mensaje" in registrado
    assert "ValueError: no se pudo insertar" in registrado
    assert TEXTO not in registrado


def test_una_conversacion_no_deja_el_texto_en_los_registros(cliente, caplog):
    configurar_registros("DEBUG")
    consentimiento = {"mayor_de_edad": True, "acepta": True}
    cliente.post("/consentimiento", json=consentimiento, headers=cabecera("luis"))
    for texto in (TEXTO, f"{TEXTO} {EXPRESION_DE_PRUEBA}"):
        respuesta = cliente.post("/chat", json={"texto": texto}, headers=cabecera("luis"))
        assert respuesta.status_code == 200
    logging.getLogger("app.prueba").info("control de captura")
    assert "control de captura" in caplog.text
    assert TEXTO not in caplog.text
