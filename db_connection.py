"""Conexión única y validada a la nueva base PostgreSQL de LubriInsight."""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv(override=True)
EXPECTED_DATABASE = "Lubricadora"


def _build_url():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        return database_url
    required = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Faltan variables de conexión en .env: " + ", ".join(missing))
    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    )


@lru_cache(maxsize=1)
def get_engine():
    return create_engine(
    _build_url(),
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=10,
    connect_args={"connect_timeout": 10},
    future=True,
)


def validate_new_database() -> dict[str, object]:
    """Verifica destino y columnas críticas antes de cargar cualquier página."""
    engine = get_engine()
    with engine.connect() as conn:
        database = conn.execute(text("SELECT current_database()")).scalar()
        schema = conn.execute(text("SELECT current_schema()")).scalar()
        tables = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
        """)).scalar()
        columns = [row[0] for row in conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'venta'
            ORDER BY ordinal_position
        """))]

    expected = {"id_venta", "cedula_cliente", "id_tipo_pago", "fecha_venta", "total"}
    missing = sorted(expected - set(columns))
    if missing:
        raise RuntimeError(
            f"La conexión apunta a '{database}', pero no es la nueva BD. "
            f"Faltan columnas en venta: {', '.join(missing)}. "
            "Configura DB_NAME=Lubricadoray reinicia Streamlit."
        )
    return {"database": database, "schema": schema, "tables": tables, "venta_columns": columns}
