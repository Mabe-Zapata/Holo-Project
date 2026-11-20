"""Resumen semanal para el tratante (HU-17a).

El modelo redacta hechos con su día de origen, siguiendo `data/prompts/prompt_resumen.md`.
Antes de devolverlos se descartan los que no citan un día real de la conversación o
que tocan temas clínicos. La respuesta indica siempre que fue generada por IA.
"""

import json
import re
from pathlib import Path

from app.core.config import obtener_configuracion
from app.services.filtros import es_consulta_clinica
from app.services.prompts import cargar_prompt_sistema
from app.services.proveedor_llm import ProveedorLLM, crear_proveedor

RUTA_PROMPT_RESUMEN = Path(__file__).resolve().parents[2] / "data" / "prompts" / "prompt_resumen.md"
MAXIMO_HECHOS = 10
MAXIMO_CARACTERES_HECHO = 200
MAXIMO_CARACTERES_MENSAJE = 500


class ResumenNoValido(Exception):
    """El modelo no devolvió un resumen con la forma esperada."""


def preparar_mensajes(mensajes: list[dict]) -> str:
    """Solo los mensajes de la persona, con su fecha, en orden cronológico."""
    lineas = []
    for mensaje in sorted(mensajes, key=lambda m: m["fecha"]):
        if mensaje["autor"] != "usuario":
            continue
        dia = mensaje["fecha"].date().isoformat()
        lineas.append(f"{dia}: {mensaje['texto'][:MAXIMO_CARACTERES_MENSAJE]}")
    return "\n".join(lineas)


def _extraer_json(crudo: str) -> dict:
    """Acepta JSON directo o envuelto en un bloque de código."""
    coincidencia = re.search(r"\{.*\}", crudo, re.DOTALL)
    if coincidencia is None:
        raise ResumenNoValido("La respuesta no contiene JSON.")
    try:
        datos = json.loads(coincidencia.group(0))
    except ValueError as error:
        raise ResumenNoValido("El JSON del resumen no es válido.") from error
    if not isinstance(datos, dict) or not isinstance(datos.get("hechos"), list):
        raise ResumenNoValido("El resumen debe tener una lista 'hechos'.")
    return datos


def parsear_hechos(crudo: str, dias_validos: set[str]) -> list[dict]:
    """Descarta lo que no cumple: día inventado, texto vacío o largo, o tema clínico."""
    hechos = []
    for hecho in _extraer_json(crudo)["hechos"]:
        if not isinstance(hecho, dict):
            continue
        dia, texto = hecho.get("dia"), hecho.get("hecho")
        if dia not in dias_validos or not isinstance(texto, str):
            continue
        texto = texto.strip()
        if not texto or len(texto) > MAXIMO_CARACTERES_HECHO:
            continue
        if es_consulta_clinica(texto):
            continue
        hechos.append({"dia": dia, "hecho": texto})
        if len(hechos) == MAXIMO_HECHOS:
            break
    return hechos


def generar_resumen(mensajes: list[dict], proveedor: ProveedorLLM) -> dict:
    """Resumen con el contrato de odds/resumen.md. Sin mensajes de la persona no se llama al modelo.

    `temas` y `patrones` quedan vacíos hasta que HU-17 los incorpore.
    """
    del_usuario = [m for m in mensajes if m["autor"] == "usuario"]
    hechos = []
    if del_usuario:
        dias = {m["fecha"].date().isoformat() for m in del_usuario}
        crudo = proveedor.responder(preparar_mensajes(del_usuario), [])
        hechos = [
            {"fecha": h["dia"], "descripcion": h["hecho"]} for h in parsear_hechos(crudo, dias)
        ]
    return {"generado_por_ia": True, "temas": [], "hechos": hechos, "patrones": []}


def crear_resumidor() -> ProveedorLLM:
    """Proveedor con el prompt de resumen. Se construye solo cuando se pide un resumen."""
    cfg = obtener_configuracion()
    prompt = cargar_prompt_sistema(RUTA_PROMPT_RESUMEN).texto
    return crear_proveedor(
        cfg.proveedor_llm,
        clave=cfg.llm_api_key,
        modelo=cfg.llm_modelo,
        url_base=cfg.llm_url_base,
        prompt=prompt,
    )
