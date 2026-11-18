from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select

from app.db import crear_motor, crear_tablas, pacientes, profesionales, usuarios, vinculos
from app.main import app
from app.repositorios.usuarios import buscar_usuario, crear_cuentas_demo


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


def contar(conexion, tabla) -> int:
    return conexion.execute(select(func.count()).select_from(tabla)).scalar_one()


def totales(conexion) -> list[int]:
    return [contar(conexion, t) for t in (usuarios, pacientes, profesionales, vinculos)]


def test_crea_las_tres_cuentas(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        assert buscar_usuario(conexion, "ana") == {
            "id": "ana",
            "nombre": "Ana",
            "rol": "usuario_estandar",
            "tratante_id": None,
        }
        assert buscar_usuario(conexion, "luis") == {
            "id": "luis",
            "nombre": "Luis",
            "rol": "paciente",
            "tratante_id": "tratante",
        }
        assert buscar_usuario(conexion, "tratante") == {
            "id": "tratante",
            "nombre": "Tratante de demostración",
            "rol": "profesional",
            "tratante_id": None,
        }


def test_luis_es_paciente_de_ansiedad_vinculado_a_la_tratante(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        # one() exige una sola fila: Ana, sin tratante, no tiene perfil de paciente.
        paciente = conexion.execute(select(pacientes)).mappings().one()
        profesional = conexion.execute(select(profesionales)).mappings().one()
        vinculo = conexion.execute(select(vinculos)).mappings().one()
    assert (paciente["usuario_id"], paciente["modulo"]) == ("luis", "ansiedad")
    assert paciente["tecnicas_permitidas"] == ["respiracion", "anclaje"]
    assert (profesional["usuario_id"], profesional["tipo"]) == ("tratante", "psicologo")
    assert (vinculo["paciente_id"], vinculo["profesional_id"], vinculo["estado"]) == (
        "luis",
        "tratante",
        "activo",
    )


def test_no_duplica_si_se_ejecuta_dos_veces(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        crear_cuentas_demo(conexion)
        assert totales(conexion) == [3, 1, 1, 1]


def test_completa_lo_que_falta_sin_modificar_lo_existente(motor):
    with motor.begin() as conexion:
        conexion.execute(
            usuarios.insert().values(
                id="ana",
                nombre="Ana editada",
                rol="usuario_estandar",
                creado_en=datetime.now(timezone.utc),
            )
        )
        crear_cuentas_demo(conexion)
        assert buscar_usuario(conexion, "ana")["nombre"] == "Ana editada"
        assert contar(conexion, usuarios) == 3


def test_no_modifica_el_perfil_ni_el_vinculo_existentes(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        conexion.execute(pacientes.update().values(nivel_sugerencia="alto"))
        conexion.execute(vinculos.update().values(estado="revocado"))
        crear_cuentas_demo(conexion)
        assert conexion.execute(select(pacientes.c.nivel_sugerencia)).scalar_one() == "alto"
        # Con el vínculo revocado, Luis ya no tiene tratante.
        assert buscar_usuario(conexion, "luis")["tratante_id"] is None


def test_buscar_usuario_inexistente(motor):
    with motor.begin() as conexion:
        crear_cuentas_demo(conexion)
        assert buscar_usuario(conexion, "desconocido") is None


def test_se_crean_al_iniciar_y_se_conservan_al_reiniciar(monkeypatch, tmp_path):
    # Archivo SQLite temporal en lugar de :memory:, que desaparece con cada motor:
    # así el segundo arranque encuentra lo que dejó el primero, sin necesitar Docker.
    url = f"sqlite:///{tmp_path / 'holo.db'}"
    monkeypatch.setattr("app.main.crear_motor", lambda: motor_sqlite(url))
    motor = motor_sqlite(url)
    try:
        with TestClient(app):  # primer arranque
            with motor.begin() as conexion:
                # Las cuentas ya existen mientras el servidor está encendido.
                assert totales(conexion) == [3, 1, 1, 1]
                conexion.execute(
                    usuarios.update().where(usuarios.c.id == "ana").values(nombre="Ana editada")
                )
        with TestClient(app):  # reinicio
            pass
        with motor.connect() as conexion:
            assert totales(conexion) == [3, 1, 1, 1]
            assert buscar_usuario(conexion, "ana")["nombre"] == "Ana editada"
            assert buscar_usuario(conexion, "luis")["tratante_id"] == "tratante"
    finally:
        motor.dispose()
