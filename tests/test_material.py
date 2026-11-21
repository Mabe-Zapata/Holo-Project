"""Carga del material etiquetado (HU-07)."""

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.pool import StaticPool

from app.db import crear_tablas, material
from app.repositorios.material import guardar_texto, listar_textos
from app.services.material import validar_lote, validar_texto
from scripts.cargar_material import cargar_desde_archivo

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_INICIAL = RAIZ / "data" / "material" / "textos_iniciales.json"


def texto(**cambios):
    base = {
        "id": "T-1",
        "titulo": "Título",
        "tema": "tema",
        "modulo": "general",
        "modo": "estandar",
        "estado": "provisional",
        "fuente": "Fuente de prueba",
        "texto": "Un texto de prueba.",
    }
    base.update(cambios)
    return base


@pytest.fixture
def motor():
    motor = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    crear_tablas(motor)
    yield motor
    motor.dispose()


def contar(motor):
    with motor.connect() as conexion:
        return conexion.execute(select(func.count()).select_from(material)).scalar()


def test_un_texto_valido_se_devuelve_limpio():
    limpio = validar_texto(texto(titulo="  Con espacios  "))

    assert limpio["titulo"] == "Con espacios"


@pytest.mark.parametrize(
    "cambio, motivo",
    [
        ({"modulo": "otro"}, "Módulo"),
        ({"modo": "admin"}, "Modo"),
        ({"estado": "publicado"}, "Estado"),
        ({"modulo": "ansiedad", "modo": "estandar"}, "modo paciente"),
        ({"titulo": "   "}, "titulo"),
        ({"texto": None}, "texto"),
    ],
)
def test_un_texto_con_etiquetas_invalidas_se_rechaza(cambio, motivo):
    with pytest.raises(ValueError, match=motivo):
        validar_texto(texto(**cambio))


def test_un_texto_sin_campos_se_rechaza():
    datos = texto()
    del datos["fuente"]

    with pytest.raises(ValueError, match="fuente"):
        validar_texto(datos)


def test_el_lote_exige_entre_cinco_y_diez_textos():
    lote = [texto(id=f"T-{n}") for n in range(4)]
    with pytest.raises(ValueError, match="entre 5 y 10"):
        validar_lote(lote)

    grande = [texto(id=f"T-{n}") for n in range(11)]
    with pytest.raises(ValueError, match="entre 5 y 10"):
        validar_lote(grande)


def test_el_lote_no_admite_identificadores_repetidos():
    lote = [texto(id=f"T-{n}") for n in range(5)]
    lote[4]["id"] = "T-0"

    with pytest.raises(ValueError, match="repetidos"):
        validar_lote(lote)


def test_el_archivo_inicial_cumple_las_reglas_de_la_historia():
    textos = validar_lote(json.loads(ARCHIVO_INICIAL.read_text(encoding="utf-8")))

    assert 5 <= len(textos) <= 10
    assert all(t["estado"] == "provisional" for t in textos)
    assert all(t["fuente"] for t in textos)
    assert all(t["modo"] == "paciente" for t in textos if t["modulo"] == "ansiedad")


def test_cargar_el_archivo_inicial_guarda_los_textos(motor):
    cantidad = cargar_desde_archivo(motor, ARCHIVO_INICIAL)

    assert cantidad == 7
    assert contar(motor) == 7


def test_volver_a_cargar_no_duplica(motor):
    cargar_desde_archivo(motor, ARCHIVO_INICIAL)
    cargar_desde_archivo(motor, ARCHIVO_INICIAL)

    assert contar(motor) == 7


def test_guardar_de_nuevo_actualiza_el_texto(motor):
    with motor.begin() as conexion:
        guardar_texto(conexion, texto(id="A-1", texto="versión uno"))
        guardar_texto(conexion, texto(id="A-1", texto="versión dos"))

    with motor.connect() as conexion:
        textos = listar_textos(conexion, ("provisional",))
    assert [t["texto"] for t in textos] == ["versión dos"]


def test_listar_filtra_por_estado(motor):
    with motor.begin() as conexion:
        guardar_texto(conexion, texto(id="B-1", estado="aprobado"))
        guardar_texto(conexion, texto(id="B-2", estado="provisional"))

    with motor.connect() as conexion:
        aprobados = listar_textos(conexion, ("aprobado",))
    assert [t["id"] for t in aprobados] == ["B-1"]
