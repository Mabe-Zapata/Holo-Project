"""Pruebas del consentimiento informado (BE-03, HU-03)."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select

from app.db import consentimientos, crear_motor, crear_tablas
from app.main import app
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


def test_primera_aceptacion_concurrente_no_falla_ni_duplica(tmp_path, monkeypatch):
    motor = crear_motor(f"sqlite:///{(tmp_path / 'concurrente.db').as_posix()}")
    monkeypatch.setattr("app.main.crear_motor", lambda: motor)
    inicio = Barrier(2)
    lecturas = Barrier(2)

    def sincronizar_lecturas(_conexion, _cursor, sentencia, _parametros, _contexto, _muchos):
        # Hace determinista la carrera si la implementación consulta antes de insertar.
        if sentencia.startswith("SELECT consentimientos.id"):
            lecturas.wait(timeout=5)

    try:
        with TestClient(app, raise_server_exceptions=False) as cliente:
            event.listen(motor, "after_cursor_execute", sincronizar_lecturas)

            def aceptar():
                inicio.wait(timeout=5)
                return cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("ana"))

            try:
                with ThreadPoolExecutor(max_workers=2) as ejecutor:
                    futuros = [ejecutor.submit(aceptar) for _ in range(2)]
                    respuestas = [futuro.result(timeout=15) for futuro in futuros]
            finally:
                event.remove(motor, "after_cursor_execute", sincronizar_lecturas)

            assert [respuesta.status_code for respuesta in respuestas] == [201, 201]
            for respuesta in respuestas:
                assert respuesta.json()["usuario_id"] == "ana"
                assert (
                    datetime.fromisoformat(respuesta.json()["aceptado_en"]).utcoffset() is not None
                )
            with motor.connect() as conexion:
                filas = (
                    conexion.execute(
                        select(consentimientos).where(consentimientos.c.usuario_id == "ana")
                    )
                    .mappings()
                    .all()
                )
            assert len(filas) == 1
            assert filas[0]["mayor_de_edad"] is True
            assert filas[0]["version_texto"] == "provisional-1"
    finally:
        motor.dispose()


def test_registrar_consentimiento_respeta_rollback_del_llamador(cliente):
    motor = cliente.app.state.motor
    with motor.connect() as conexion:
        transaccion = conexion.begin()
        registrar_consentimiento(conexion, "ana", True)
        transaccion.rollback()
        assert conexion.execute(select(consentimientos)).first() is None

    respuesta = cliente.post("/consentimiento", headers=cabecera("ana"), json=CONSENTIMIENTO)
    assert respuesta.status_code == 201
    with motor.connect() as conexion:
        antes = dict(conexion.execute(select(consentimientos)).mappings().one())
        conexion.rollback()
        transaccion = conexion.begin()
        registrar_consentimiento(conexion, "ana", True, version_texto="rollback-only")
        transaccion.rollback()
        despues = dict(conexion.execute(select(consentimientos)).mappings().one())
        assert despues == antes
