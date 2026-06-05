"""Tests del resena_service (Mongo + Postgres + Neo4j + Redis)."""
import pytest


def _setup_viaje_finalizado_y_personas(postgres_clean, mongo_clean, cassandra_clean,
                                        neo4j_clean, redis_clean):
    """Setup completo: usuario, conductor, vehiculo, viaje finalizado."""
    from src.services import auth_service, vehiculo_service, viaje_service
    uid = auth_service.register_usuario("u@m.com", "p", "Juan Pérez")
    cid = auth_service.register_conductor("c@m.com", "p", "Ana Gómez", "LIC-R")
    vid = vehiculo_service.registrar(cid, "R1", "Toyota", "Corolla")
    viaje_id = viaje_service.solicitar(uid, cid, vid,
                                        {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 20)
    return uid, cid, viaje_id


def test_crear_inserta_resena_en_mongo(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service
    from src.repositories import resena_repo

    uid, cid, viaje_id = _setup_viaje_finalizado_y_personas(
        postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    rid = resena_service.crear(
        viaje_id=viaje_id, tipo="U_A_C",
        autor_id=uid, autor_nombre="Juan Pérez",
        destinatario_id=cid, destinatario_nombre="Ana Gómez",
        rating=5, comentario="Excelente",
    )
    r = resena_repo.get_by_id(rid)
    assert r["rating"] == 5
    assert r["tipo"] == "U_A_C"
    assert r["autor"]["id"] == uid


def test_crear_actualiza_rating_promedio_postgres(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service
    from src.repositories import conductor_repo

    uid, cid, viaje_id = _setup_viaje_finalizado_y_personas(
        postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    resena_service.crear(
        viaje_id, "U_A_C", uid, "Juan", cid, "Ana", 5, "ok",
    )
    cond = conductor_repo.get_by_id(cid)
    assert cond["rating_promedio"] == pytest.approx(5.0)


def test_crear_promedia_varias_resenas(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    """Si vienen 2 reseñas con ratings 4 y 5, el promedio del destinatario debe ser 4.5."""
    from src.services import resena_service, auth_service, vehiculo_service, viaje_service
    from src.repositories import conductor_repo

    cid = auth_service.register_conductor("c@m.com", "p", "Ana", "LIC-R")
    vid = vehiculo_service.registrar(cid, "R1", "M", "M")

    for i, rating in enumerate([4, 5]):
        uid = auth_service.register_usuario(f"u{i}@m.com", "p", f"U{i}")
        viaje_id = viaje_service.solicitar(uid, cid, vid,
                                            {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
        viaje_service.iniciar(viaje_id)
        viaje_service.finalizar(viaje_id, 5, 20)
        resena_service.crear(viaje_id, "U_A_C", uid, f"U{i}", cid, "Ana", rating, "ok")

    assert conductor_repo.get_by_id(cid)["rating_promedio"] == pytest.approx(4.5)


def test_crear_invalida_cache_top3(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service
    from src.repositories import cache_repo

    cache_repo.set_cache("top3_resenadores", [{"x": 1}])
    assert cache_repo.get_cache("top3_resenadores") is not None

    uid, cid, viaje_id = _setup_viaje_finalizado_y_personas(
        postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    resena_service.crear(viaje_id, "U_A_C", uid, "U", cid, "C", 5, "ok")

    assert cache_repo.get_cache("top3_resenadores") is None


def test_crear_sobre_viaje_no_finalizado_lanza_error(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service, auth_service, vehiculo_service, viaje_service
    from src.utils.errors import EstadoInvalido

    uid = auth_service.register_usuario("u@m.com", "p", "U")
    cid = auth_service.register_conductor("c@m.com", "p", "C", "LIC")
    vid = vehiculo_service.registrar(cid, "P", "M", "M")
    # No finalizamos el viaje: queda en PENDIENTE
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    with pytest.raises(EstadoInvalido):
        resena_service.crear(viaje_id, "U_A_C", uid, "U", cid, "C", 5, "ok")
