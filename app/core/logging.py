"""Configuración de los registros (BE-15): nunca deben contener el texto de los mensajes.

- Solo el código de Holo (loggers "app.*", obtenidos con logging.getLogger(__name__)) usa el nivel
  de HOLO_NIVEL_REGISTROS. Las bibliotecas quedan en WARNING, porque en DEBUG algunas escriben lo
  que envían, como el prompt al modelo.
- Las trazas de excepciones muestran el tipo y solo la primera línea del mensaje: las siguientes
  pueden traer datos, como el DETAIL de PostgreSQL con la fila o el input de una validación.

Regla del equipo: nunca registrar el texto de un mensaje, ni siquiera en DEBUG.
"""

import logging
import traceback

FORMATO = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def _traza_sin_detalle(exc: BaseException | None) -> str:
    # shortcut: si el código pone el texto en la primera línea de una excepción, se verá;
    # para usuarios reales conviene ocultar también esa línea.
    bloques, vistas = [], set()
    while exc is not None and id(exc) not in vistas:
        vistas.add(id(exc))
        primera = (str(exc).splitlines() or [""])[0]
        traza = "".join(traceback.format_tb(exc.__traceback__))
        bloques.append(
            f"Traceback (most recent call last):\n{traza}{type(exc).__name__}: {primera}"
        )
        exc = exc.__cause__ or (None if exc.__suppress_context__ else exc.__context__)
    return "\nCausada por:\n".join(bloques)


class _SinDetalleDeExcepciones(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.exc_info and record.exc_info[1] is not None:
            # El formateador usa exc_text si ya existe, también el de uvicorn.
            record.exc_text = _traza_sin_detalle(record.exc_info[1])
        return True


_FILTRO = _SinDetalleDeExcepciones()


def configurar_registros(nivel: str) -> None:
    # Primero: un nivel inválido falla aquí, antes de cambiar nada más.
    logging.getLogger("app").setLevel(nivel.upper())
    raiz = logging.getLogger()
    if not raiz.handlers:
        manejador = logging.StreamHandler()
        manejador.setFormatter(logging.Formatter(FORMATO))
        raiz.addHandler(manejador)
    raiz.setLevel(logging.WARNING)
    # Los manejadores que ya existen, como los de uvicorn, también ocultan el detalle.
    existentes = logging.root.manager.loggerDict.values()
    for registrador in [raiz, *(r for r in existentes if isinstance(r, logging.Logger))]:
        for manejador in registrador.handlers:
            manejador.addFilter(_FILTRO)
