from sqlalchemy import inspect

from app.db import crear_motor, crear_tablas, verificar_conexion


def test_conexion_en_memoria():
    motor = crear_motor("sqlite:///:memory:")
    assert verificar_conexion(motor)


def test_crear_tablas_del_primer_sprint():
    motor = crear_motor("sqlite:///:memory:")
    crear_tablas(motor)
    tablas = set(inspect(motor).get_table_names())
    esperadas = {
        "usuarios",
        "pacientes",
        "profesionales",
        "vinculos",
        "consentimientos",
        "mensajes",
    }
    assert esperadas <= tablas


def test_crear_tablas_es_idempotente():
    motor = crear_motor("sqlite:///:memory:")
    crear_tablas(motor)
    crear_tablas(motor)
    assert "mensajes" in inspect(motor).get_table_names()
