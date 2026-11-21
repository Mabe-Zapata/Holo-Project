"""Pasa a la base los eventos de crisis que quedaron en la cola local (HU-16).

Es idempotente: si un evento ya está guardado, no se duplica. Sin consentimiento vigente
al momento de sincronizar, el evento se descarta y se registra solo su identificador.
"""

import logging
import threading
from datetime import datetime

from sqlalchemy import Engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from app.repositorios.alertas import registrar_alerta
from app.repositorios.consentimiento import tiene_consentimiento
from app.repositorios.mensajes import buscar_mensaje_por_evento, guardar_mensaje
from app.services.almacen import ahora
from app.services.cola import ColaPendientes
from app.services.riesgo import TEXTO_CRISIS

registro = logging.getLogger(__name__)
SUFIJO_RESPUESTA = ":resp"


def aplicar_evento(conexion: Connection, evento: dict) -> bool:
    """Guarda el evento de crisis. Devuelve False si se descartó por falta de consentimiento."""
    uid = evento["usuario_id"]
    eid = evento["id_evento"]
    if buscar_mensaje_por_evento(conexion, uid, eid) is not None:
        return True
    if not tiene_consentimiento(conexion, uid):
        registro.info("Evento %s descartado: la cuenta no tiene consentimiento.", eid)
        return False
    fecha = datetime.fromisoformat(evento["fecha"])
    guardar_mensaje(conexion, uid, "usuario", "mensaje", evento["texto"], fecha, id_evento=eid)
    registrar_alerta(conexion, uid, "alto", evento["texto"], fecha, id_evento=eid)
    guardar_mensaje(
        conexion,
        uid,
        "asistente",
        "crisis",
        TEXTO_CRISIS,
        ahora(),
        id_evento=eid + SUFIJO_RESPUESTA,
    )
    return True


def sincronizar(motor: Engine, cola: ColaPendientes) -> int:
    """Aplica los eventos pendientes. Devuelve cuántos quedaron resueltos."""
    resueltos = 0
    for evento in cola.pendientes():
        eid = evento["id_evento"]
        try:
            with motor.begin() as conexion:
                aplicar_evento(conexion, evento)
        except SQLAlchemyError as error:
            registro.warning(
                "No se pudo sincronizar (%s): la cola conserva sus eventos.",
                type(error).__name__,
            )
            return resueltos
        except Exception:
            # Un evento malformado no bloquea a los demás; queda en la cola para revisión.
            registro.exception("No se pudo aplicar el evento %s; se conserva en la cola.", eid)
            continue
        cola.quitar(eid)
        resueltos += 1
    return resueltos


class Sincronizador:
    """Reintenta la cola en segundo plano hasta que se detiene."""

    def __init__(self, motor: Engine, cola: ColaPendientes, intervalo_s: float):
        self._motor = motor
        self._cola = cola
        self._intervalo = intervalo_s
        self._parar = threading.Event()
        self._hilo: threading.Thread | None = None

    def iniciar(self) -> None:
        self._hilo = threading.Thread(target=self._bucle, name="sincronizador", daemon=True)
        self._hilo.start()

    def detener(self) -> None:
        self._parar.set()
        if self._hilo is not None:
            self._hilo.join(timeout=5)

    def _bucle(self) -> None:
        while not self._parar.is_set():
            try:
                sincronizar(self._motor, self._cola)
            except Exception:
                registro.exception("Fallo inesperado al sincronizar la cola.")
            self._parar.wait(self._intervalo)
