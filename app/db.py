"""Conexión a PostgreSQL con SQLAlchemy y tablas del primer sprint (BE-01).

Las pruebas usan SQLite en memoria a través de la misma función, sin Docker.
El modelo completo del MVP está en docs/diagrama-bd.dbml; aquí solo van las tablas del sprint 1.
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine

from app.core.config import obtener_configuracion

metadata = MetaData()

usuarios = Table(
    "usuarios",
    metadata,
    Column("id", String(50), primary_key=True),
    Column("nombre", String(100), nullable=False),
    Column("rol", String(30), nullable=False),
    Column("creado_en", DateTime(timezone=True), nullable=False),
)

pacientes = Table(
    "pacientes",
    metadata,
    Column("usuario_id", String(50), ForeignKey("usuarios.id"), primary_key=True),
    Column("modulo", String(50), nullable=True),
    Column("nivel_sugerencia", String(20), nullable=False, default="medio"),
    Column("tecnicas_permitidas", JSON, nullable=False),
    Column("creado_en", DateTime(timezone=True), nullable=False),
)

profesionales = Table(
    "profesionales",
    metadata,
    Column("usuario_id", String(50), ForeignKey("usuarios.id"), primary_key=True),
    Column("tipo", String(30), nullable=False),
    Column("registro_profesional", String(50), nullable=True),
    Column("verificado", Boolean, nullable=False, default=False),
)

vinculos = Table(
    "vinculos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("paciente_id", String(50), ForeignKey("pacientes.usuario_id"), nullable=False),
    Column("profesional_id", String(50), ForeignKey("profesionales.usuario_id"), nullable=False),
    Column("codigo_invitacion", String(20), unique=True, nullable=True),
    Column("estado", String(20), nullable=False),
    Column("creado_en", DateTime(timezone=True), nullable=False),
    UniqueConstraint("paciente_id", "profesional_id", name="uq_vinculo_paciente_profesional"),
)

consentimientos = Table(
    "consentimientos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("usuario_id", String(50), ForeignKey("usuarios.id"), nullable=False, unique=True),
    Column("version_texto", String(20), nullable=False),
    Column("mayor_de_edad", Boolean, nullable=False),
    Column("aceptado_en", DateTime(timezone=True), nullable=False),
)

mensajes = Table(
    "mensajes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("usuario_id", String(50), ForeignKey("usuarios.id"), nullable=False),
    Column("autor", String(20), nullable=False),
    Column("tipo", String(20), nullable=False),
    Column("texto", Text, nullable=False),
    Column("creado_en", DateTime(timezone=True), nullable=False),
)

Index("ix_mensajes_usuario_fecha", mensajes.c.usuario_id, mensajes.c.creado_en)


def crear_motor(url: str | None = None) -> Engine:
    """Crea el motor de SQLAlchemy. Sin URL usa HOLO_URL_BASE_DATOS."""
    if url is None:
        url = obtener_configuracion().url_base_datos
    # hide_parameters: los errores y registros de SQL no muestran el texto de los mensajes (BE-15).
    return create_engine(url, pool_pre_ping=True, hide_parameters=True)


def verificar_conexion(motor: Engine) -> bool:
    """Devuelve True si la base responde."""
    with motor.connect() as conexion:
        return conexion.execute(text("SELECT 1")).scalar() == 1


def crear_tablas(motor: Engine) -> None:
    """Crea las tablas que falten. No modifica ni borra las existentes."""
    metadata.create_all(motor)
