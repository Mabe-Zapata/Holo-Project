from app.services.riesgo import (
    RECURSOS_AYUDA,
    RUTA_TEXTO_CRISIS,
    TEXTO_CRISIS,
    cargar_expresiones,
    cargar_texto_crisis,
    es_riesgo_alto,
    normalizar,
)


def test_normalizar_quita_tildes_y_mayusculas():
    assert normalizar("  ÁNIMO   Difícil ") == "animo dificil"


def test_es_riesgo_alto_ignora_tildes():
    assert es_riesgo_alto("Tengo una EXPRESIÓN marcada", ["expresion marcada"])
    assert not es_riesgo_alto("Hoy fue un buen día", ["expresion marcada"])


def test_cargar_expresiones_ignora_comentarios(tmp_path):
    archivo = tmp_path / "lista.txt"
    archivo.write_text("# comentario\n\nPrimera Expresión\n", encoding="utf-8")
    assert cargar_expresiones(str(archivo)) == ["primera expresion"]


def test_cargar_expresiones_sin_archivo():
    assert cargar_expresiones("no-existe.txt") == []


def test_lista_de_prueba_tiene_al_menos_quince_expresiones():
    ruta = RUTA_TEXTO_CRISIS.parent / "expresiones_riesgo.txt"
    assert len(cargar_expresiones(str(ruta))) >= 15


def test_detecta_riesgo_con_mayusculas_y_tildes_en_la_lista_real():
    ruta = RUTA_TEXTO_CRISIS.parent / "expresiones_riesgo.txt"
    expresiones = cargar_expresiones(str(ruta))
    assert es_riesgo_alto("QUIERO   MORIR", expresiones)
    assert es_riesgo_alto("No le encuentro sentido a VIVIR", expresiones)
    assert not es_riesgo_alto("Hoy fue un buen día", expresiones)


def test_texto_de_crisis_y_recursos_se_leen_del_archivo():
    texto, recursos = cargar_texto_crisis(RUTA_TEXTO_CRISIS)
    assert texto == TEXTO_CRISIS
    assert texto.startswith("[Texto provisional")
    assert "ECU 911" in texto
    assert [r["telefono"] for r in recursos] == ["911", "171"]
    assert recursos == RECURSOS_AYUDA
