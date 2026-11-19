from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from app.db import crear_motor, crear_tablas
from app.repositorios.mensajes import guardar_mensaje, listar_mensajes
from app.repositorios.usuarios import crear_cuentas_demo

BASE = datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc)


def motor_sqlite(url: str):
    """Motor SQLite con las claves foráneas activas, que PostgreSQL siempre comprueba."""
    motor = crear_motor(url)
    event.listen(motor, "connect", _activar_claves_foraneas)
    return motor


def _activar_claves_foraneas(conexion_dbapi, _registro):
    cursor = conexion_dbapi.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def motor():
    motor = motor_sqlite("sqlite:///:memory:")
    crear_tablas(motor)
    yield motor
    motor.dispose()


def sin_zona(fecha: datetime) -> datetime:
    """SQLite devuelve las fechas sin zona horaria; se comparan sin ella."""
    return fecha.replace(tzinfo=None)


def test_guardar_y_listar_devuelve_los_datos(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        guardar_mensaje(conexion, "ana", "usuario", "mensaje", "Hola, ¿cómo estás?", BASE)
        mensajes = listar_mensajes(conexion, "ana")
    assert len(mensajes) == 1
    assert set(mensajes[0]) == {"autor", "texto", "fecha", "tipo"}
    assert mensajes[0]["autor"] == "usuario"
    assert mensajes[0]["texto"] == "Hola, ¿cómo estás?"
    assert mensajes[0]["tipo"] == "mensaje"
    assert sin_zona(mensajes[0]["fecha"]) == sin_zona(BASE)


def test_ordena_cronologicamente_aunque_se_inserten_desordenados(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        guardar_mensaje(conexion, "ana", "usuario", "mensaje", "tercero", BASE + timedelta(hours=2))
        guardar_mensaje(conexion, "ana", "usuario", "mensaje", "primero", BASE)
        guardar_mensaje(conexion, "ana", "asistente", "respuesta", "segundo", BASE + timedelta(hours=1))
        textos = [m["texto"] for m in listar_mensajes(conexion, "ana")]
    assert textos == ["primero", "segundo", "tercero"]


def test_con_la_misma_fecha_respeta_el_orden_de_insercion(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        for texto in ("uno", "dos", "tres"):
            guardar_mensaje(conexion, "ana", "usuario", "mensaje", texto, BASE)
        textos = [m["texto"] for m in listar_mensajes(conexion, "ana")]
    assert textos == ["uno", "dos", "tres"]


def test_un_usuario_no_ve_los_mensajes_de_otro(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        guardar_mensaje(conexion, "ana", "usuario", "mensaje", "mensaje de Ana", BASE)
        guardar_mensaje(conexion, "luis", "usuario", "mensaje", "mensaje de Luis", BASE)
        de_ana = listar_mensajes(conexion, "ana")
        de_luis = listar_mensajes(conexion, "luis")
    assert [m["texto"] for m in de_ana] == ["mensaje de Ana"]
    assert [m["texto"] for m in de_luis] == ["mensaje de Luis"]


def test_usuario_sin_mensajes_devuelve_lista_vacia(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        assert listar_mensajes(conexion, "ana") == []


def test_sin_fecha_usa_la_hora_actual(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        antes = datetime.now(timezone.utc)
        guardar_mensaje(conexion, "ana", "usuario", "mensaje", "ahora")
        despues = datetime.now(timezone.utc)
        fecha = listar_mensajes(conexion, "ana")[0]["fecha"]
    assert sin_zona(antes) <= sin_zona(fecha) <= sin_zona(despues)


def test_usuario_inexistente_lanza_error_de_integridad(motor):
    with pytest.raises(IntegrityError):
        with motor.begin() as conexion:
            guardar_mensaje(conexion, "desconocido", "usuario", "mensaje", "hola", BASE)
