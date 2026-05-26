"""MongoDB connection — singleton."""
from pymongo import MongoClient
from pymongo.database import Database
from src.config import settings
from src.utils.logger import logger

_client: MongoClient | None = None
_DB_NAME = "uber_tp"


def get_client() -> MongoClient:
    """Devuelve el cliente Mongo (lo crea la primera vez)."""
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URL)
        logger.info("Conexion a MongoDB establecida")
    return _client


def get_db() -> Database:
    """Devuelve la database `uber_tp`."""
    return get_client()[_DB_NAME]


def check() -> bool:
    """Devuelve True si la conexion y el ping funcionan."""
    try:
        get_client().admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"Mongo check failed: {e}")
        return False
