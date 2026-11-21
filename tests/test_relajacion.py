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


@pytest.mark.parametrize("tecnica", ["", "Respiracion", "respiración", " anclaje "])
def test_el_nombre_de_la_tecnica_debe_ser_exacto(tecnica):
    with pytest.raises(ValueError):
        siguiente_paso(tecnica, paso=0, confirmacion=True)


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_empezar_no_requiere_confirmacion(tecnica):
    primero = siguiente_paso(tecnica, paso=0, confirmacion=True)

    assert primero.texto == TECNICAS[tecnica][0]
    assert primero.paso == 1


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_cada_paso_se_repite_hasta_que_el_usuario_confirma(tecnica):
    textos = []
    paso = 0
    resultado = siguiente_paso(tecnica, paso=paso, confirmacion=False)
    textos.append(resultado.texto)
    paso = resultado.paso
    while not resultado.terminada:
        repetido = siguiente_paso(tecnica, paso=paso, confirmacion=False)
        assert repetido.texto == textos[-1]
        assert repetido.paso == paso
        resultado = siguiente_paso(tecnica, paso=paso, confirmacion=True)
        paso = resultado.paso
        textos.append(resultado.texto)

    assert textos[:-1] == list(TECNICAS[tecnica])


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_sin_confirmacion_en_el_ultimo_paso_no_termina_la_tecnica(tecnica):
    ultimo = len(TECNICAS[tecnica])

    resultado = siguiente_paso(tecnica, paso=ultimo, confirmacion=False)

    assert not resultado.terminada
    assert resultado.paso == ultimo
    assert resultado.texto == TECNICAS[tecnica][-1]


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_una_vez_terminada_confirmar_de_nuevo_sigue_terminada(tecnica):
    ultimo = len(TECNICAS[tecnica])

    primero = siguiente_paso(tecnica, paso=ultimo, confirmacion=True)
    segundo = siguiente_paso(tecnica, paso=primero.paso, confirmacion=True)

    assert primero.terminada and segundo.terminada
    assert segundo.paso == ultimo


@pytest.mark.parametrize("tecnica", ["respiracion", "anclaje"])
def test_los_pasos_son_textos_no_vacios_y_sin_repetidos(tecnica):
    pasos = TECNICAS[tecnica]

    assert all(p.strip() for p in pasos)
    assert len(pasos) == len(set(pasos))


@pytest.mark.parametrize("paso", [-1, 99])
def test_paso_fuera_de_rango_tambien_falla_sin_confirmacion(paso):
    with pytest.raises(ValueError):
        siguiente_paso("anclaje", paso=paso, confirmacion=False)
