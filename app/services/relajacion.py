"""Técnicas de relajación guiadas paso a paso (HU-11).

El avance depende de la confirmación del usuario: sin ella, el paso se repite.
"""

from dataclasses import dataclass

TECNICAS: dict[str, tuple[str, ...]] = {
    "respiracion": (
        "Siéntate cómodamente y apoya los pies en el suelo.",
        "Inhala por la nariz contando hasta cuatro, sin forzar el aire.",
        "Sostén el aire contando hasta cuatro.",
        "Exhala lentamente por la boca contando hasta seis. Repite el ciclo si lo necesitas.",
    ),
    "anclaje": (
        "Mira a tu alrededor y nombra cinco cosas que puedes ver.",
        "Nombra cuatro cosas que puedes tocar y siente su textura.",
        "Nombra tres sonidos que puedes escuchar ahora mismo.",
        "Nombra dos olores o sabores que notas.",
        "Nombra una cosa buena que tienes cerca. Respira una vez más despacio.",
    ),
}


@dataclass(frozen=True)
class PasoRelajacion:
    texto: str
    paso: int
    terminada: bool


def siguiente_paso(tecnica: str, paso: int, confirmacion: bool) -> PasoRelajacion:
    """Devuelve el paso a mostrar según el último paso mostrado y la confirmación del usuario.

    `paso` es el número del último paso mostrado (0 al empezar).
    """
    if tecnica not in TECNICAS:
        raise ValueError(f"técnica desconocida: {tecnica}")
    pasos = TECNICAS[tecnica]
    if not 0 <= paso <= len(pasos):
        raise ValueError(f"paso fuera de rango: {paso}")

    if paso == 0:
        return PasoRelajacion(texto=pasos[0], paso=1, terminada=False)
    if not confirmacion:
        return PasoRelajacion(texto=pasos[paso - 1], paso=paso, terminada=False)
    if paso == len(pasos):
        return PasoRelajacion(
            texto="Has terminado la técnica. ¿Cómo te sientes ahora?", paso=paso, terminada=True
        )
    return PasoRelajacion(texto=pasos[paso], paso=paso + 1, terminada=False)
