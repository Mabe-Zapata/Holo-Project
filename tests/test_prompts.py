from pathlib import Path

import pytest

from app.services.riesgo import normalizar
from app.services.prompts import RUTA_PROMPT_SISTEMA, cargar_prompt_sistema


def test_el_prompt_declara_su_version():
    prompt = cargar_prompt_sistema()
    assert prompt.version == "1"


def test_el_prompt_se_lee_desde_el_archivo():
    prompt = cargar_prompt_sistema()
    assert prompt.texto == RUTA_PROMPT_SISTEMA.read_text(encoding="utf-8")


def test_el_prompt_define_rol_tono_y_limites():
    texto = normalizar(cargar_prompt_sistema().texto)
    assert "inteligencia artificial" in texto
    assert "diagnostic" in texto
    assert "medicacion" in texto
    assert "fragmentos" in texto


def test_sin_version_el_prompt_se_rechaza(tmp_path: Path):
    archivo = tmp_path / "prompt.md"
    archivo.write_text("# Prompt sin versión\n", encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_prompt_sistema(archivo)


def test_archivo_inexistente_falla_en_lugar_de_usar_un_prompt_vacio(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        cargar_prompt_sistema(tmp_path / "no-existe.md")
