from app.services.riesgo import cargar_expresiones, es_riesgo_alto, normalizar


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
