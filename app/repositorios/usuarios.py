"""Repositorio de usuarios con las cuentas de demostración (BE-02).

El MVP no tiene registro ni contraseñas: la aplicación ofrece tres cuentas ficticias
que se eligen en la pantalla inicial. Al iniciar el servidor se crean las que falten;
las que ya existen no se modifican. Como el resto de los repositorios, cada función
recibe la conexión y la transacción la abre quien llama, por ejemplo con `motor.begin()`.
"""

from datetime import datetime, timezone

from sqlalchemy import ColumnElement, Table, select
from sqlalchemy.engine import Connection

from app.db import pacientes, profesionales, usuarios, vinculos

# Datos ficticios. Los valores de rol, tipo y estado siguen docs/diagrama-bd.dbml.
CUENTAS_DEMO = (
    {"id": "ana", "nombre": "Ana", "rol": "usuario_estandar"},
    {"id": "luis", "nombre": "Luis", "rol": "paciente"},
    {"id": "tratante", "nombre": "Tratante de demostración", "rol": "profesional"},
)
# Modo paciente de Luis: módulo de ansiedad (RF-11) y las dos técnicas guiadas (RF-10).
PACIENTE_DEMO = {
    "usuario_id": "luis",
    "modulo": "ansiedad",
    "nivel_sugerencia": "medio",
    "tecnicas_permitidas": ["respiracion", "anclaje"],
}
PROFESIONAL_DEMO = {
    "usuario_id": "tratante",
    "tipo": "psicologo",
    "registro_profesional": None,
    "verificado": False,
}
VINCULO_DEMO = {"paciente_id": "luis", "profesional_id": "tratante", "estado": "activo"}


def crear_cuentas_demo(conexion: Connection) -> None:
    """Crea lo que falte de las cuentas de demostración, el perfil de Luis y su vínculo."""
    ahora = datetime.now(timezone.utc)
    for cuenta in CUENTAS_DEMO:
        _insertar_si_falta(
            conexion, usuarios, usuarios.c.id == cuenta["id"], {**cuenta, "creado_en": ahora}
        )
    _insertar_si_falta(
        conexion,
        pacientes,
        pacientes.c.usuario_id == PACIENTE_DEMO["usuario_id"],
        {**PACIENTE_DEMO, "creado_en": ahora},
    )
    _insertar_si_falta(
        conexion,
        profesionales,
        profesionales.c.usuario_id == PROFESIONAL_DEMO["usuario_id"],
        PROFESIONAL_DEMO,
    )
    _insertar_si_falta(
        conexion,
        vinculos,
        (vinculos.c.paciente_id == VINCULO_DEMO["paciente_id"])
        & (vinculos.c.profesional_id == VINCULO_DEMO["profesional_id"]),
        {**VINCULO_DEMO, "creado_en": ahora},
    )


def buscar_usuario(conexion: Connection, usuario_id: str) -> dict | None:
    """Devuelve la cuenta con el id de su tratante (si tiene un vínculo activo), o None."""
    fila = (
        conexion.execute(
            select(usuarios.c.id, usuarios.c.nombre, usuarios.c.rol).where(
                usuarios.c.id == usuario_id
            )
        )
        .mappings()
        .first()
    )
    if fila is None:
        return None
    tratante_id = conexion.execute(
        select(vinculos.c.profesional_id).where(
            vinculos.c.paciente_id == usuario_id, vinculos.c.estado == "activo"
        )
    ).scalar()
    return {**fila, "tratante_id": tratante_id}


def _insertar_si_falta(
    conexion: Connection, tabla: Table, condicion: ColumnElement[bool], valores: dict
) -> None:
    if conexion.execute(select(tabla).where(condicion).limit(1)).first() is None:
        conexion.execute(tabla.insert().values(**valores))
