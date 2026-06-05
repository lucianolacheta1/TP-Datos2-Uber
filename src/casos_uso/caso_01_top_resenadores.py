"""Caso de uso 1: top 3 usuarios con más reseñas.

Base principal: Mongo (resenas) + enriquecimiento desde Postgres (nombres).
Cache: Redis con TTL 5 min.
"""
from src.repositories import resena_repo, cache_repo, usuario_repo

CACHE_KEY = "top3_resenadores"
CACHE_TTL = 300  # 5 min


def ejecutar() -> list[dict]:
    """Devuelve top 3 reseñadores, enriquecido con nombre desde Postgres.

    Formato: [{autor_id, cantidad, nombre}, ...]
    """
    # 1. Cache hit?
    cached = cache_repo.get_cache(CACHE_KEY)
    if cached is not None:
        return cached

    # 2. Aggregation en Mongo
    top = resena_repo.top_autores(n=3, tipo="U_A_C")

    # 3. Enriquecer con nombre desde Postgres
    for item in top:
        user = usuario_repo.get_by_id(item["autor_id"])
        item["nombre"] = user["nombre"] if user else "(desconocido)"

    # 4. Cachear
    cache_repo.set_cache(CACHE_KEY, top, ttl_seconds=CACHE_TTL)
    return top
