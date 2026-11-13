from tests.conftest import EXPRESION_DE_PRUEBA, cabecera

CONSENTIMIENTO = {"mayor_de_edad": True, "acepta": True}


def test_salud(cliente):
    r = cliente.get("/salud")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"


def test_cuenta_desconocida(cliente):
    r = cliente.get("/chat/historial", headers=cabecera("nadie"))
    assert r.status_code == 401


def test_chat_exige_consentimiento(cliente):
    r = cliente.post("/chat", json={"texto": "hola"}, headers=cabecera("ana"))
    assert r.status_code == 403


def test_consentimiento_rechazado_si_no_acepta(cliente):
    r = cliente.post(
        "/consentimiento", json={"mayor_de_edad": True, "acepta": False}, headers=cabecera("ana")
    )
    assert r.status_code == 400


def test_chat_responde_y_guarda_historial(cliente):
    assert (
        cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("ana")).status_code
        == 201
    )
    r = cliente.post("/chat", json={"texto": "Estoy estresada"}, headers=cabecera("ana"))
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["tipo"] == "respuesta"
    assert cuerpo["riesgo"] == "sin_riesgo"

    historial = cliente.get("/chat/historial", headers=cabecera("ana")).json()
    assert [m["autor"] for m in historial] == ["usuario", "asistente"]


def test_riesgo_alto_muestra_crisis_y_registra_alerta(cliente):
    cliente.post("/consentimiento", json=CONSENTIMIENTO, headers=cabecera("luis"))
    r = cliente.post(
        "/chat",
        json={"texto": f"Mensaje con {EXPRESION_DE_PRUEBA.upper()}"},
        headers=cabecera("luis"),
    )
    cuerpo = r.json()
    assert cuerpo["tipo"] == "crisis"
    assert cuerpo["riesgo"] == "alto"
    assert {rec["telefono"] for rec in cuerpo["recursos"]} == {"911", "171"}

    vista = cliente.get("/tratante/paciente", headers=cabecera("tratante")).json()
    assert vista["paciente_id"] == "luis"
    assert len(vista["alertas"]) == 1


def test_vista_del_tratante_solo_para_tratante(cliente):
    r = cliente.get("/tratante/paciente", headers=cabecera("ana"))
    assert r.status_code == 403


def test_resumen_pendiente(cliente):
    r = cliente.post("/resumen", headers=cabecera("tratante"))
    assert r.status_code == 501
