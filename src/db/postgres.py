"""Postgres connection — singleton."""
import psycopg
from src.config import settings
from src.utils.logger import logger

_conn = None


def get_conn() -> psycopg.Connection:
    """Devuelve la conexion Postgres (la crea la primera vez)."""
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg.connect(settings.POSTGRES_URL, autocommit=True)
        logger.info("Conexion a Postgres establecida")
    return _conn


def check() -> bool:
    """Devuelve True si la conexion y la query basica funcionan."""
    try:
        with get_conn().cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)
    except Exception as e:
        logger.error(f"Postgres check failed: {e}")
        return False
