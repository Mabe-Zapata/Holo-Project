"""Interfaz única hacia el modelo de lenguaje (RNF-12).

El resto del backend solo conoce `ProveedorLLM`. Para usar Gemini, Groq u
otro proveedor se agrega aquí una clase nueva y se registra en
`crear_proveedor`.
"""

from typing import Protocol


class ProveedorLLM(Protocol):
    def responder(self, mensaje: str, fragmentos: list[str]) -> str:
        """Redacta una respuesta a partir del mensaje y los fragmentos recuperados."""
        ...


class ProveedorEco:
    """Proveedor de prueba: devuelve el mensaje recibido. No usa ningún modelo."""

    def responder(self, mensaje: str, fragmentos: list[str]) -> str:
        return f"[eco] {mensaje}"


def crear_proveedor(nombre: str) -> ProveedorLLM:
    if nombre == "eco":
        return ProveedorEco()
    raise ValueError(f"Proveedor de modelo no soportado: {nombre}")
