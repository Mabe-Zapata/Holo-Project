"""Formato de la entrada del modelo: el material y el mensaje, entre etiquetas (IA-01)."""


def _neutralizar(texto: str) -> str:
    # Ningún "<" del contenido puede abrir o cerrar una etiqueta del formato.
    return texto.replace("<", "&lt;")


def formatear_entrada(mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
    """Arma la entrada del modelo: el material con su identificador y el mensaje."""
    lineas = [f"[{id_}] {_neutralizar(texto)}" for id_, texto in fragmentos]
    material = "\n".join(lineas) + "\n" if lineas else ""
    return f"<material>\n{material}</material>\n<mensaje>\n{_neutralizar(mensaje)}\n</mensaje>"
