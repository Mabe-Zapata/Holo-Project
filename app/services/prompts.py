"""Prompt del sistema versionado (IA-01): rol, tono y límites del asistente.

El texto vive en data/prompts/prompt_sistema.md y lo aprueba la especialista.
`formatear_entrada` define cómo se entregan el mensaje y el material al modelo:
el contenido del usuario nunca puede cerrar las etiquetas.
"""

from dataclasses import dataclass
from pathlib import Path

RUTA_PROMPT_SISTEMA = (
    Path(__file__).resolve().parents[2] / "data" / "prompts" / "prompt_sistema.md"
)


@dataclass(frozen=True)
class PromptSistema:
    version: str
    texto: str


def cargar_prompt_sistema(ruta: Path = RUTA_PROMPT_SISTEMA) -> PromptSistema:
    """Lee el prompt del archivo. Sin "Versión:" se rechaza: nunca se usa un prompt vacío."""
    contenido = ruta.read_text(encoding="utf-8")
    for linea in contenido.splitlines():
        if linea.startswith("Versión:"):
            version = linea.split(":", 1)[1].strip()
            if version:
                return PromptSistema(version=version, texto=contenido)
    raise ValueError(f"{ruta.name} debe declarar una línea 'Versión: <número>'")


def _neutralizar(texto: str) -> str:
    # Ningún "<" del contenido puede abrir o cerrar una etiqueta del formato.
    return texto.replace("<", "&lt;")


def formatear_entrada(mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
    """Arma la entrada del modelo: el material con su identificador y el mensaje."""
    material = "\n".join(f"[{id_}] {_neutralizar(texto)}" for id_, texto in fragmentos)
    bloque_material = f"<material>\n{material}\n</material>" if material else "<material>\n</material>"
    return f"{bloque_material}\n<mensaje>\n{_neutralizar(mensaje)}\n</mensaje>"
