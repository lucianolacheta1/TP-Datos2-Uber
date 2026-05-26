"""Redis connection — singleton.

Convenciones de claves usadas en el proyecto:

    session:{token}             -> JSON con datos de la sesion (TTL 10 min)
    vehiculo:{id}:pos           -> "lat,lon" (TTL 30 s)
    cache:top3_resenadores      -> JSON (TTL 5 min)
    cache:viajes_promedio       -> JSON (TTL 5 min)
"""
import redis
from src.config import settings
from src.utils.logger import logger

_client: redis.Redis | None = None


def get_client() -> redis.Redis:
    """Devuelve el cliente Redis (lo crea la primera vez)."""
    global _client
    if _client is None:
        _client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        logger.info("Conexion a Redis establecida")
    return _client


def check() -> bool:
    """Devuelve True si el ping funciona."""
    try:
        return bool(get_client().ping())
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        return False
