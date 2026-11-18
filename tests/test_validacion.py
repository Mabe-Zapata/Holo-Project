import pytest

from app.schemas.chat import MensajeEntrada
from tests.conftest import cabecera

MSG_VACIO = "El mensaje no puede estar vacío."
MSG_LARGO = "El mensaje no puede superar los 2000 caracteres."


def _mensajes(respuesta) -> str:
    return " ".join(str(e.get("msg", "")) for e in respuesta.json()["detail"])


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("", MSG_VACIO),
        ("   ", MSG_VACIO),
        ("a" * 2001, MSG_LARGO),
    ],
)
def test_chat_rechaza_texto_invalido(cliente, texto, esperado):
    r = cliente.post("/chat", json={"texto": texto}, headers=cabecera("ana"))
    assert r.status_code == 422
    assert esperado in _mensajes(r)


def test_esquema_acepta_2000_caracteres():
    assert len(MensajeEntrada(texto="a" * 2000).texto) == 2000


def test_esquema_no_recorta_el_texto():
    assert MensajeEntrada(texto="  hola ").texto == "  hola "
