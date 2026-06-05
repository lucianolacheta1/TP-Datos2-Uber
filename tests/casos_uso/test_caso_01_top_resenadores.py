"""Tests del caso de uso 1: top 3 reseñadores (Mongo + Redis cache)."""
from datetime import datetime, UTC


def _crear_resenas(autor_id: str, cantidad: int):
    """Helper: inserta N reseñas U_A_C de un autor en Mongo."""
    from src.repositories import resena_repo
    for _ in range(cantidad):
        resena_repo.crear({
            "viaje_id": "v",
            "tipo": "U_A_C",
            "autor":        {"id": autor_id, "nombre": f"Autor {autor_id}"},
            "destinatario": {"id": "c1", "nombre": "Conductor"},
            "rating": 5,
            "comentario": "ok",
            "timestamp": datetime.now(UTC),
        })


def test_devuelve_top_3_ordenado_desc(postgres_clean, mongo_clean, redis_clean):
    from src.repositories import usuario_repo
    from src.casos_uso import caso_01_top_resenadores

    # 3 usuarios reales en Postgres para enriquecer
    a_id = usuario_repo.crear("a@m.com", "h", "Andrea")
    b_id = usuario_repo.crear("b@m.com", "h", "Beto")
    c_id = usuario_repo.crear("c@m.com", "h", "Carla")
    d_id = usuario_repo.crear("d@m.com", "h", "Diana")
    _crear_resenas(a_id, 5)
    _crear_resenas(b_id, 3)
    _crear_resenas(c_id, 2)
    _crear_resenas(d_id, 1)

    top = caso_01_top_resenadores.ejecutar()
    assert len(top) == 3
    assert [t["autor_id"] for t in top] == [a_id, b_id, c_id]
    assert top[0]["cantidad"] == 5
    assert top[0]["nombre"] == "Andrea"


def test_cachea_en_redis(postgres_clean, mongo_clean, redis_clean):
    from src.repositories import usuario_repo, cache_repo
    from src.casos_uso import caso_01_top_resenadores

    uid = usuario_repo.crear("x@m.com", "h", "X")
    _crear_resenas(uid, 1)
    caso_01_top_resenadores.ejecutar()

    cached = cache_repo.get_cache("top3_resenadores")
    assert cached is not None
    assert cached[0]["autor_id"] == uid


def test_segunda_llamada_usa_cache(postgres_clean, mongo_clean, redis_clean):
    """Si hay cache, no toca Mongo."""
    from src.repositories import cache_repo
    from src.casos_uso import caso_01_top_resenadores

    cache_repo.set_cache("top3_resenadores", [{"autor_id": "FAKE", "cantidad": 99, "nombre": "Fake"}])
    top = caso_01_top_resenadores.ejecutar()
    # Devuelve el cache, no datos reales (que están vacíos)
    assert top[0]["autor_id"] == "FAKE"
    assert top[0]["cantidad"] == 99


def test_sin_resenas_devuelve_lista_vacia(postgres_clean, mongo_clean, redis_clean):
    from src.casos_uso import caso_01_top_resenadores
    assert caso_01_top_resenadores.ejecutar() == []
