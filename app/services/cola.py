"""Cola local de eventos de crisis que la base no pudo guardar (HU-16).

Cada línea es un evento JSON. Se escribe con `fsync` antes de responder a la persona, así
un corte del proceso no pierde un evento ya confirmado. La cola contiene texto sensible:
su archivo no debe subirse al repositorio ni compartirse.
"""

import json
import logging
import os
import threading
from pathlib import Path

registro = logging.getLogger(__name__)


class ColaPendientes:
    def __init__(self, ruta: str | Path):
        self._ruta = Path(ruta)
        self._cerrojo = threading.Lock()

    def encolar(self, evento: dict) -> None:
        """Agrega un evento al final de la cola y lo confirma en disco."""
        linea = json.dumps(evento, ensure_ascii=False)
        with self._cerrojo:
            self._ruta.parent.mkdir(parents=True, exist_ok=True)
            with self._ruta.open("a", encoding="utf-8") as archivo:
                archivo.write(linea + "\n")
                archivo.flush()
                os.fsync(archivo.fileno())

    def pendientes(self) -> list[dict]:
        """Eventos en orden de llegada. Las líneas dañadas se omiten y se registran."""
        with self._cerrojo:
            return self._leer()

    def quitar(self, id_evento: str) -> None:
        """Quita un evento ya aplicado. Reescribe el archivo de forma atómica."""
        with self._cerrojo:
            eventos = [e for e in self._leer() if e["id_evento"] != id_evento]
            temporal = self._ruta.with_suffix(".tmp")
            with temporal.open("w", encoding="utf-8") as archivo:
                for evento in eventos:
                    archivo.write(json.dumps(evento, ensure_ascii=False) + "\n")
                archivo.flush()
                os.fsync(archivo.fileno())
            os.replace(temporal, self._ruta)

    def _leer(self) -> list[dict]:
        if not self._ruta.exists():
            return []
        eventos = []
        lineas = self._ruta.read_text(encoding="utf-8").splitlines()
        for numero, linea in enumerate(lineas, start=1):
            if not linea.strip():
                continue
            try:
                evento = json.loads(linea)
            except json.JSONDecodeError:
                # Registro sin contenido del mensaje (BE-15): solo el número de línea.
                registro.error("La línea %s de la cola no es JSON válido; se omite.", numero)
                continue
            if not isinstance(evento, dict) or not evento.get("id_evento"):
                registro.error("La línea %s de la cola no tiene id_evento; se omite.", numero)
                continue
            eventos.append(evento)
        return eventos
