"""Tests del caso de uso 7: reseñas con rating 5 o menor a 2 (Mongo)."""
from datetime import datetime, UTC


def _resena(rating: int):
    return {
        "viaje_id": "v", "tipo": "U_A_C",
        "autor": {"id": "a", "nombre": "A"},
        "destinatario": {"id": "d", "nombre": "D"},
        "rating": rating, "comentario": "x",
        "timestamp": datetime.now(UTC),
    }


def test_devuelve_solo_extremos(mongo_clean):
    from src.repositories import resena_repo
    from src.casos_uso import caso_07_resenas_extremas

    resena_repo.crear(_resena(5))
    resena_repo.crear(_resena(1))
    resena_repo.crear(_resena(3))  # ignorada
    resena_repo.crear(_resena(4))  # ignorada
    resena_repo.crear(_resena(5))

    extremas = caso_07_resenas_extremas.ejecutar()
    ratings = sorted(r["rating"] for r in extremas)
    assert ratings == [1, 5, 5]


def test_sin_resenas_devuelve_lista_vacia(mongo_clean):
    from src.casos_uso import caso_07_resenas_extremas
    assert caso_07_resenas_extremas.ejecutar() == []
