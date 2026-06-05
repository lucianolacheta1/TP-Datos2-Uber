"""Repository de cache (Redis). Sesiones, ultima posicion y cache de queries."""
import json
from src.db.redis_db import get_client


def _k_session(token: str) -> str:
    return f"session:{token}"


def _k_pos(vehiculo_id: str) -> str:
    return f"vehiculo:{vehiculo_id}:pos"


def _k_cache(key: str) -> str:
    return f"cache:{key}"


# ---- Sesiones ----

def set_session(token: str, data: dict, ttl_seconds: int = 600) -> None:
    """Guarda una sesión con TTL."""
    get_client().setex(_k_session(token), ttl_seconds, json.dumps(data))


def get_session(token: str) -> dict | None:
    val = get_client().get(_k_session(token))
    return json.loads(val) if val else None


def delete_session(token: str) -> None:
    get_client().delete(_k_session(token))


# ---- Ultima posicion del vehiculo ----

def set_ultima_pos(vehiculo_id: str, lat: float, lon: float,
                   ttl_seconds: int = 30) -> None:
    get_client().setex(_k_pos(vehiculo_id), ttl_seconds, f"{lat},{lon}")


def get_ultima_pos(vehiculo_id: str) -> tuple[float, float] | None:
    val = get_client().get(_k_pos(vehiculo_id))
    if val is None:
        return None
    lat_s, lon_s = val.split(",")
    return (float(lat_s), float(lon_s))


# ---- Cache de queries pesadas ----

def set_cache(key: str, data, ttl_seconds: int = 300) -> None:
    """Cachea cualquier objeto serializable JSON."""
    get_client().setex(_k_cache(key), ttl_seconds, json.dumps(data))


def get_cache(key: str):
    val = get_client().get(_k_cache(key))
    return json.loads(val) if val else None


def invalidar(key: str) -> None:
    """Elimina una entrada del cache."""
    get_client().delete(_k_cache(key))
