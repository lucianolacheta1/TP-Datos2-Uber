"""Tests del viaje_service (Mongo + Cassandra + Neo4j + Redis)."""
import pytest
import uuid
from datetime import datetime, UTC


def _setup_entidades(postgres_clean, neo4j_clean):
    """Crea un usuario, conductor y vehiculo de prueba. Devuelve sus ids."""
    from src.services import auth_service, vehiculo_service
    uid = auth_service.register_usuario("user@m.com", "p", "User")
    cid = auth_service.register_conductor("driver@m.com", "p", "Driver", "LIC-V")
    vid = vehiculo_service.registrar(cid, "ABC123D", "Toyota", "Corolla")
    return uid, cid, vid


# ---- solicitar ----

def test_solicitar_crea_documento_en_mongo(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(
        uid, cid, vid,
        origen={"lat": -34.6, "lon": -58.4, "direccion": "Palermo"},
        destino={"lat": -34.55, "lon": -58.45, "direccion": "Belgrano"},
    )
    v = viaje_repo.get_by_id(viaje_id)
    assert v is not None
    assert v["estado"] == "PENDIENTE"
    assert v["usuario_id"] == uid
    assert v["conductor_id"] == cid


def test_solicitar_incluye_snapshots(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(
        uid, cid, vid,
        {"lat": -34.6, "lon": -58.4}, {"lat": -34.5, "lon": -58.5},
    )
    v = viaje_repo.get_by_id(viaje_id)
    assert v["usuario_snapshot"]["nombre"] == "User"
    assert v["conductor_snapshot"]["nombre"] == "Driver"


def test_solicitar_con_usuario_inexistente_lanza_error(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.utils.errors import UsuarioInexistente

    _, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    with pytest.raises(UsuarioInexistente):
        viaje_service.solicitar(
            "00000000-0000-0000-0000-000000000000", cid, vid,
            {"lat": 0, "lon": 0}, {"lat": 0, "lon": 0},
        )


# ---- iniciar ----

def test_iniciar_cambia_estado(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    ok = viaje_service.iniciar(viaje_id)
    assert ok is True
    assert viaje_repo.get_by_id(viaje_id)["estado"] == "EN_CURSO"


# ---- finalizar ----

def test_finalizar_actualiza_mongo(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, distancia_km=8.5, duracion_min=22)

    v = viaje_repo.get_by_id(viaje_id)
    assert v["estado"] == "FINALIZADO"
    assert v["distancia_km"] == 8.5
    assert v["duracion_min"] == 22


def test_finalizar_proyecta_a_cassandra(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import actividad_repo
    from src.repositories import conductor_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 15)

    ultima = actividad_repo.get_ultima(uuid.UUID(cid))
    assert ultima is not None
    # viaje_id es un ObjectId de Mongo; en Cassandra se guarda como UUID
    # (relleno con ceros a 32 hex, igual que viaje_service._viaje_id_a_uuid).
    assert ultima["ultimo_viaje_id"] == uuid.UUID(viaje_id.rjust(32, "0"))


def test_finalizar_incrementa_arista_neo4j(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import grafo_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 15)

    coincidencias = grafo_repo.coincidencias(min_viajes=1)
    assert len(coincidencias) == 1
    assert coincidencias[0]["pasajero_id"] == uid
    assert coincidencias[0]["conductor_id"] == cid
    assert coincidencias[0]["viajes"] == 1


def test_finalizar_dos_viajes_misma_pareja_incrementa_arista(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import grafo_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    for _ in range(3):
        viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
        viaje_service.iniciar(viaje_id)
        viaje_service.finalizar(viaje_id, 5, 15)
    coincidencias = grafo_repo.coincidencias(min_viajes=2)
    assert coincidencias[0]["viajes"] == 3
