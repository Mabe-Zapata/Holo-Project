"""Evalúa los mensajes de prueba y deja los resultados en docs/resultados-pruebas.md (HU-21).

Uso (desde la raíz del repositorio):
    python scripts/evaluar_mensajes.py

Termina con código 1 si algún mensaje no se evalúa como se espera.
Los mensajes y las listas son provisionales: la revisión de la especialista queda pendiente.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.services.filtros import es_consulta_clinica  # noqa: E402
from app.services.riesgo import cargar_expresiones, es_riesgo_alto  # noqa: E402

ARCHIVO_MENSAJES = RAIZ / "tests" / "datos" / "mensajes_prueba.json"
ARCHIVO_EXPRESIONES = RAIZ / "data" / "expresiones_riesgo.txt"
ARCHIVO_RESULTADOS = RAIZ / "docs" / "resultados-pruebas.md"


def evaluar(mensajes: list[dict], expresiones: list[str]) -> list[dict]:
    """Ejecuta los detectores sobre cada mensaje y compara con su categoría esperada.

    - riesgo: debe activar la detección de riesgo.
    - clinica: debe activar el filtro clínico.
    - habitual: no debe activar ninguno de los dos.
    """
    resultados = []
    for mensaje in mensajes:
        riesgo = es_riesgo_alto(mensaje["texto"], expresiones)
        clinica = es_consulta_clinica(mensaje["texto"])
        categoria = mensaje["categoria"]
        if categoria == "riesgo":
            ok = riesgo
        elif categoria == "clinica":
            ok = clinica
        else:
            ok = not riesgo and not clinica
        resultados.append(
            {
                "id": mensaje["id"],
                "categoria": categoria,
                "texto": mensaje["texto"],
                "riesgo": riesgo,
                "clinica": clinica,
                "ok": ok,
            }
        )
    return resultados


def resumen_markdown(resultados: list[dict]) -> str:
    """Tabla de conteos por categoría y lista de los mensajes que fallaron."""
    lineas = [
        "# Resultados de los mensajes de prueba",
        "",
        "Mensajes ficticios y listas provisionales. Falta la revisión de la especialista.",
        "",
        "| Categoría | Total | Aciertos | Fallos |",
        "| --- | --- | --- | --- |",
    ]
    for categoria in ("riesgo", "clinica", "habitual"):
        del_grupo = [r for r in resultados if r["categoria"] == categoria]
        aciertos = sum(r["ok"] for r in del_grupo)
        lineas.append(
            f"| {categoria} | {len(del_grupo)} | {aciertos} | {len(del_grupo) - aciertos} |"
        )
    fallos = [r for r in resultados if not r["ok"]]
    lineas += ["", "## Fallos", ""]
    if not fallos:
        lineas.append("Ninguno.")
    for r in fallos:
        lineas.append(f"- {r['id']} ({r['categoria']}): {r['texto']}")
    return "\n".join(lineas) + "\n"


def main() -> int:
    mensajes = json.loads(ARCHIVO_MENSAJES.read_text(encoding="utf-8"))
    expresiones = cargar_expresiones(str(ARCHIVO_EXPRESIONES))
    resultados = evaluar(mensajes, expresiones)
    ARCHIVO_RESULTADOS.write_text(resumen_markdown(resultados), encoding="utf-8")
    fallos = sum(not r["ok"] for r in resultados)
    correctos = len(resultados) - fallos
    print(f"{correctos}/{len(resultados)} como se esperaba. Resultados en {ARCHIVO_RESULTADOS}")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
