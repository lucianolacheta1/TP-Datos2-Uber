"""Neo4j (Aura) connection — singleton driver."""
from neo4j import GraphDatabase, Driver
from src.config import settings
from src.utils.logger import logger  # configura y silencia loggers ruidosos al importar

_driver: Driver | None = None


def get_driver() -> Driver:
    """Devuelve el driver Neo4j (lo crea la primera vez)."""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        logger.info("Conexion a Neo4j (Aura) establecida")
    return _driver


def check() -> bool:
    """Devuelve True si el driver y la query basica funcionan."""
    try:
        with get_driver().session() as s:
            record = s.run("RETURN 1 AS ok").single()
            return record is not None and record["ok"] == 1
    except Exception as e:
        logger.error(f"Neo4j check failed: {e}")
        return False
