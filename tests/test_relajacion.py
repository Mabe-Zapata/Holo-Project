import pytest

from app.services.relajacion import TECNICAS, siguiente_paso


def _recorrer(tecnica: str) -> list[str]:
    """Recorre la técnica completa confirmando cada paso."""
    textos = []
    paso = 0
    while True:
        resultado = siguiente_paso(tecnica, paso, confirmacion=True)
        textos.append(resultado.texto)
        paso = resultado.paso
        if resultado.terminada:
            return textos


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_empieza_por_el_primer_paso(tecnica):
    resultado = siguiente_paso(tecnica, paso=0, confirmacion=False)

    assert resultado.texto == TECNICAS[tecnica][0]
    assert resultado.paso == 1
    assert not resultado.terminada


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_sin_confirmacion_repite_el_mismo_paso(tecnica):
    primero = siguiente_paso(tecnica, paso=0, confirmacion=False)

    repetido = siguiente_paso(tecnica, paso=primero.paso, confirmacion=False)

    assert repetido.texto == primero.texto
    assert repetido.paso == primero.paso


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_con_confirmacion_avanza_al_siguiente_paso(tecnica):
    primero = siguiente_paso(tecnica, paso=0, confirmacion=False)

    segundo = siguiente_paso(tecnica, paso=primero.paso, confirmacion=True)

    assert segundo.texto == TECNICAS[tecnica][1]
    assert segundo.paso == 2


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_recorre_la_secuencia_completa_en_orden(tecnica):
    pasos = TECNICAS[tecnica]

    recorrido = _recorrer(tecnica)

    assert recorrido[: len(pasos)] == list(pasos)
    assert len(recorrido) == len(pasos) + 1  # el último mensaje cierra la técnica


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_la_ultima_respuesta_marca_la_tecnica_como_terminada(tecnica):
    ultimo_paso = len(TECNICAS[tecnica])

    cierre = siguiente_paso(tecnica, paso=ultimo_paso, confirmacion=True)

    assert cierre.terminada
    assert cierre.paso == ultimo_paso


def test_las_dos_tecnicas_tienen_al_menos_tres_pasos_cada_una():
    assert set(TECNICAS) == {"respiracion", "anclaje"}
    assert all(len(pasos) >= 3 for pasos in TECNICAS.values())


def test_tecnica_desconocida_falla():
    with pytest.raises(ValueError):
        siguiente_paso("meditacion", paso=0, confirmacion=True)


@pytest.mark.parametrize("paso", [-1, 99])
def test_paso_fuera_de_rango_falla(paso):
    with pytest.raises(ValueError):
        siguiente_paso("respiracion", paso=paso, confirmacion=True)
