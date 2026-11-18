"""Interfaz única hacia el modelo de lenguaje (RNF-12).

El resto del backend solo conoce `ProveedorLLM`. `ProveedorCompatibleOpenAI` sirve a
cualquier API de chat compatible con OpenAI (por ejemplo, Groq) y usa solo la biblioteca
estándar. El prompt del sistema se entrega al crear el proveedor, no en cada llamada.
"""

import json
import urllib.request
from collections.abc import Callable
from typing import Protocol

from app.services.formato import formatear_entrada

TIEMPO_MAXIMO = 20  # segundos


class ProveedorNoDisponible(Exception):
    """El modelo no respondió o respondió algo que no se puede leer."""


class ProveedorLLM(Protocol):
    def responder(self, mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
        """Redacta una respuesta a partir del mensaje y los fragmentos (id, texto)."""
        ...


class ProveedorEco:
    """Proveedor de prueba: devuelve el mensaje recibido. No usa ningún modelo."""

    def responder(self, mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
        return f"[eco] {mensaje}"


class ProveedorDiferido:
    """Construye el proveedor solo al responder, después de los controles del chat."""

    def __init__(self, fabrica: Callable[[], ProveedorLLM]) -> None:
        self._fabrica = fabrica

    def responder(self, mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
        try:
            proveedor = self._fabrica()
        except (ValueError, OSError) as error:
            raise ProveedorNoDisponible("El proveedor no está disponible.") from error
        return proveedor.responder(mensaje, fragmentos)


def _enviar_json(url: str, cabeceras: dict, cuerpo: bytes, timeout: int) -> dict:
    peticion = urllib.request.Request(url, data=cuerpo, headers=cabeceras, method="POST")
    with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


class ProveedorCompatibleOpenAI:
    def __init__(
        self,
        url_base: str,
        api_key: str,
        modelo: str,
        prompt: str,
        transporte: Callable[[str, dict, bytes, int], dict] = _enviar_json,
        timeout: int = TIEMPO_MAXIMO,
    ) -> None:
        self._url = url_base.rstrip("/") + "/chat/completions"
        self._cabeceras = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "holo-backend/0.1",
        }
        self._modelo = modelo
        self._prompt = prompt
        self._transporte = transporte
        self._timeout = timeout

    def responder(self, mensaje: str, fragmentos: list[tuple[str, str]]) -> str:
        cuerpo = {
            "model": self._modelo,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": self._prompt},
                {"role": "user", "content": formatear_entrada(mensaje, fragmentos)},
            ],
        }
        try:
            datos = self._transporte(
                self._url,
                self._cabeceras,
                json.dumps(cuerpo).encode("utf-8"),
                self._timeout,
            )
            texto = datos["choices"][0]["message"]["content"]
            if not isinstance(texto, str) or not texto.strip():
                raise ValueError("El modelo no devolvió un texto válido.")
        except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
            # El detalle técnico no sale del backend: solo se informa que el modelo no respondió.
            raise ProveedorNoDisponible("El modelo no respondió.") from error
        return texto.strip()


def crear_proveedor(
    nombre: str,
    *,
    clave: str = "",
    modelo: str = "",
    url_base: str = "",
    prompt: str = "",
) -> ProveedorLLM:
    if nombre == "eco":
        return ProveedorEco()
    if nombre == "groq":
        if not clave or not modelo:
            raise ValueError("El proveedor real necesita HOLO_LLM_API_KEY y HOLO_LLM_MODELO.")
        return ProveedorCompatibleOpenAI(
            url_base=url_base, api_key=clave, modelo=modelo, prompt=prompt
        )
    raise ValueError(f"Proveedor de modelo no soportado: {nombre}")
