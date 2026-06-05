"""Caso de uso 7: reseñas con rating 5 o menor a 2.

Base: Mongo (resenas).
"""
from src.repositories import resena_repo


def ejecutar() -> list[dict]:
    """Devuelve las reseñas extremas (rating = 5 o rating < 2)."""
    return resena_repo.buscar_por_rating_extremo()
