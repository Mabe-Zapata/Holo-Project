"""Pruebas del consentimiento informado (BE-03, HU-03)."""

from datetime import datetime

from sqlalchemy import create_engine, select

from app.db import consentimientos, crear_tablas
from app.repositorios.consentimiento import (
    buscar_fecha_aceptacion,
    registrar_consentimiento,
    tiene_consentimiento,
)
from tests.conftest import cabecera

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}


def test_registrar_consentimiento(cliente):
    """POST /consentimiento registra la aceptación y devuelve su fecha."""
    respuesta = cliente.post(
        "/consentimiento",
        json=CONSENTIMIENTO,
        headers=cabecera("ana"),
    )

    assert respuesta.status_code == 201

    datos = respuesta.json()
    assert datos["usuario_id"] == "ana"
    assert datos["aceptado_en"] is not None

    # Verifica que la fecha devuelta sea válida.
    fecha = datetime.fromisoformat(datos["aceptado_en"])
    assert isinstance(fecha, datetime)


def test_rechazar_consentimiento_menor_de_edad(cliente):
    """Un usuario menor de edad no puede registrar consentimiento."""
    respuesta = cliente.post(
        "/consentimiento",
        json={"mayor_de_edad": False, "acepta": True},
        headers=cabecera("ana"),
    )

    assert respuesta.status_code == 400


def test_rechazar_consentimiento_sin_aceptacion(cliente):
    """No se registra consentimiento si el usuario no acepta."""
    respuesta = cliente.post(
        "/consentimiento",
        json={"mayor_de_edad": True, "acepta": False},
        headers=cabecera("ana"),
    )

    assert respuesta.status_code == 400


def test_chat_sin_consentimiento(cliente):
    """El chat devuelve HTTP 403 cuando no existe consentimiento."""
    respuesta = cliente.post(
        "/chat",
        json={"texto": "Hola"},
        headers=cabecera("ana"),
    )

    assert respuesta.status_code == 403


def test_consentimiento_se_guarda_en_base_de_datos(cliente):
    """Comprueba que la aceptación queda registrada en SQLite."""
    respuesta = cliente.post(
        "/consentimiento",
        json=CONSENTIMIENTO,
        headers=cabecera("ana"),
    )

    assert respuesta.status_code == 201

    motor = cliente.app.state.motor

    with motor.connect() as conexion:
        registro = (
            conexion.execute(select(consentimientos).where(consentimientos.c.usuario_id == "ana"))
            .mappings()
            .first()
        )

    assert registro is not None
    assert registro["mayor_de_edad"] is True
    assert registro["version_texto"] == "provisional-1"
    assert registro["aceptado_en"] is not None


def test_actualizar_consentimiento_sin_duplicados(cliente):
    """Aceptar nuevamente actualiza el registro sin duplicarlo."""
    for _ in range(2):
        respuesta = cliente.post(
            "/consentimiento",
            json=CONSENTIMIENTO,
            headers=cabecera("ana"),
        )
        assert respuesta.status_code == 201

    motor = cliente.app.state.motor

    with motor.connect() as conexion:
        registros = conexion.execute(
            select(consentimientos).where(consentimientos.c.usuario_id == "ana")
        ).all()

    assert len(registros) == 1


def test_persistencia_tras_reiniciar_conexion(tmp_path):
    """El consentimiento permanece al cerrar y reabrir la base SQLite."""

    ruta = tmp_path / "consentimientos.db"
    url = f"sqlite:///{ruta.as_posix()}"

    # Primera conexión: crear tablas y registrar consentimiento.
    motor = create_engine(url)

    try:
        crear_tablas(motor)

        # La tabla consentimientos tiene una clave foránea a usuarios.
        # Creamos una cuenta de demostración para respetar esa relación.
        from app.repositorios.usuarios import crear_cuentas_demo

        with motor.begin() as conexion:
            crear_cuentas_demo(conexion)
            registrar_consentimiento(
                conexion=conexion,
                usuario_id="ana",
                mayor_de_edad=True,
            )
    finally:
        motor.dispose()

    # Segunda conexión: comprobar que la fecha sigue guardada.
    motor_reiniciado = create_engine(url)

    try:
        with motor_reiniciado.connect() as conexion:
            fecha = buscar_fecha_aceptacion(conexion, "ana")
            aceptado = tiene_consentimiento(conexion, "ana")

        assert fecha is not None
        assert isinstance(fecha, datetime)
        assert aceptado is True
    finally:
        motor_reiniciado.dispose()
