"""Consultas seguras y tolerantes a una BD aún no configurada."""

import re

import pandas as pd
import streamlit as st
from sqlalchemy import text


FALLBACK_METRICS = {
    "clientes": "—", "ventas": "—", "productos": "—", "ingresos": "—",
    "clientes_detail": "Configure PostgreSQL", "ventas_detail": "Configure PostgreSQL",
    "productos_detail": "Configure PostgreSQL", "ingresos_detail": "Configure PostgreSQL",
}

_PALABRAS_PROHIBIDAS = {
    "insert", "update", "delete", "drop", "alter", "truncate",
    "create", "grant", "revoke", "call", "merge", "replace",
    "vacuum", "reindex", "copy",
}


def get_overview_metrics() -> tuple[dict[str, str], bool]:
    """Obtiene métricas reales cuando existe conexión; si no, no bloquea la interfaz."""
    try:
        from db_connection import get_engine
        engine = get_engine()
        queries = {
            "clientes": "SELECT COUNT(*) AS value FROM cliente",
            "ventas": "SELECT COUNT(*) AS value FROM venta",
            "productos": "SELECT COUNT(*) AS value FROM producto",
            "ingresos": "SELECT COALESCE(SUM(total), 0) AS value FROM venta",
        }
        values = {key: pd.read_sql(query, engine).iloc[0, 0] for key, query in queries.items()}
        return {
            "clientes": f"{int(values['clientes']):,}", "ventas": f"{int(values['ventas']):,}",
            "productos": f"{int(values['productos']):,}", "ingresos": f"${float(values['ingresos']):,.2f}",
            "clientes_detail": "Registros activos", "ventas_detail": "Transacciones registradas",
            "productos_detail": "Catálogo disponible", "ingresos_detail": "Facturación acumulada",
        }, True
    except Exception:
        return FALLBACK_METRICS, False


@st.cache_data(ttl=300, show_spinner=False)
def query_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Ejecuta consultas de lectura desde una única capa reutilizable."""
    from db_connection import get_engine

    return pd.read_sql_query(text(sql), get_engine(), params=params or {})


def get_engine_cached():
    """Punto único de acceso al engine para operaciones de escritura."""
    from db_connection import get_engine
    return get_engine()


def execute_write(sql: str, params: dict | None = None):
    """Ejecuta un INSERT/UPDATE/DELETE dentro de una transacción."""
    engine = get_engine_cached()
    with engine.begin() as conn:
        return conn.execute(text(sql), params or {})


def insert_returning_id(sql: str, params: dict, id_column: str) -> int:
    """Ejecuta un INSERT ... RETURNING y devuelve el id generado."""
    engine = get_engine_cached()
    with engine.begin() as conn:
        result = conn.execute(text(sql + f" RETURNING {id_column}"), params)
        return result.scalar()


def write_df(df: pd.DataFrame, table: str, if_exists: str = "append"):
    """Escribe un DataFrame completo a una tabla (usado para cargas masivas)."""
    engine = get_engine_cached()
    df.to_sql(table, engine, if_exists=if_exists, index=False, method="multi", chunksize=500)


def clear_query_cache():
    """Limpia la caché de lecturas; llamar despues de escribir para reflejar cambios."""
    query_df.clear()


def is_read_only_sql(sql: str) -> bool:
    """True solo si `sql` es una única sentencia de lectura (SELECT, WITH o EXPLAIN),
    sin sentencias adicionales encadenadas ni palabras de escritura/DDL en el texto.

    Usada por el Laboratorio SQL del Centro de Datos, para que el usuario pueda
    escribir consultas libres sin poder modificar ni borrar datos por accidente.
    """
    if not sql or not sql.strip():
        return False

    limpio = sql.strip()

    # Rechaza múltiples sentencias: solo se permite un ';' final opcional.
    sin_punto_final = limpio[:-1] if limpio.endswith(";") else limpio
    if ";" in sin_punto_final:
        return False

    primera_palabra = re.match(r"[a-zA-Z]+", sin_punto_final)
    if not primera_palabra or primera_palabra.group(0).lower() not in ("select", "with", "explain"):
        return False

    # Aunque empiece con SELECT/WITH, un CTE puede ocultar un INSERT/UPDATE/DELETE con
    # RETURNING, o la consulta podría intentar DDL disfrazado. Por seguridad, se bloquea
    # si aparece cualquier palabra de escritura/estructura en cualquier parte del texto.
    tokens = set(re.findall(r"[a-zA-Z_]+", sin_punto_final.lower()))
    if tokens & _PALABRAS_PROHIBIDAS:
        return False

    return True