"""Caso de uso 4: tiempo promedio de viajes (en minutos).

Base: Cassandra (viajes_finalizados_por_dia).
Cache: Redis con TTL 5 min.
"""
from src.repositories import actividad_repo, cache_repo

CACHE_KEY = "viajes_promedio"
CACHE_TTL = 300  # 5 min


def ejecutar() -> float:
    """Devuelve el promedio de duración (min) de viajes finalizados."""
    cached = cache_repo.get_cache(CACHE_KEY)
    if cached is not None:
        return cached

    promedio = actividad_repo.promedio_duracion()
    cache_repo.set_cache(CACHE_KEY, promedio, ttl_seconds=CACHE_TTL)
    return promedio
