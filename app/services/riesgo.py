"""Revisión de riesgo por lista de expresiones (RF-23) y texto de crisis (RF-24).

La lista de expresiones y el texto de crisis los define y aprueba la
especialista. Lo que hay aquí es provisional.
"""

import unicodedata
from pathlib import Path

RUTA_TEXTO_CRISIS = Path(__file__).resolve().parents[2] / "data" / "texto_crisis.md"


def cargar_texto_crisis(ruta: Path) -> tuple[str, list[dict]]:
    """Lee el texto fijo y los recursos de data/texto_crisis.md (HU-14).

    Los recursos son líneas "- nombre | teléfono | descripción" bajo "## Recursos".
    """
    cuerpo, _, bloque_recursos = ruta.read_text(encoding="utf-8").partition("## Recursos")
    texto = " ".join(cuerpo.replace("## Texto", "", 1).split())
    recursos = []
    for linea in bloque_recursos.splitlines():
        if linea.strip().startswith("- "):
            nombre, telefono, descripcion = (p.strip() for p in linea.strip()[2:].split("|"))
            recursos.append({"nombre": nombre, "telefono": telefono, "descripcion": descripcion})
    return texto, recursos


TEXTO_CRISIS, RECURSOS_AYUDA = cargar_texto_crisis(RUTA_TEXTO_CRISIS)


def normalizar(texto: str) -> str:
    """Pasa a minúsculas y quita tildes para comparar sin diferencias de escritura."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())


def cargar_expresiones(ruta: str) -> list[str]:
    """Lee una expresión por línea; ignora líneas vacías y comentarios (#)."""
    archivo = Path(ruta)
    if not archivo.exists():
        return []
    expresiones = []
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            expresiones.append(normalizar(linea))
    return expresiones


def es_riesgo_alto(mensaje: str, expresiones) -> bool:
    texto = normalizar(mensaje)
    return any(expresion in texto for expresion in expresiones)
