"""Tests del reconciliacion_service."""
import pytest


@pytest.mark.skip(
    reason="Depende de auth_service/vehiculo_service/viaje_service (otros duenos), "
           "aun no implementados. Quitar el skip cuando existan."
)
def test_sync_neo4j_desde_mongo_reconstruye_aristas(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    """Después de borrar las aristas en Neo4j, sync_neo4j_desde_mongo las recrea."""
    from src.services import auth_service, vehiculo_service, viaje_service
    from src.services import reconciliacion_service
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver

    # Crear 3 viajes finalizados de una pareja (U1-C1) y 1 de otra (U2-C1)
    u1 = auth_service.register_usuario("u1@m.com", "p", "U1")
    u2 = auth_service.register_usuario("u2@m.com", "p", "U2")
    c1 = auth_service.register_conductor("c1@m.com", "p", "C1", "LIC")
    v1 = vehiculo_service.registrar(c1, "P1", "M", "M")
    for u in [u1, u1, u1, u2]:
        vid = viaje_service.solicitar(u, c1, v1, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
        viaje_service.iniciar(vid)
        viaje_service.finalizar(vid, 5, 15)

    # Borrar todas las aristas VIAJO_CON en Neo4j (simulando drift)
    with get_driver().session() as s:
        s.run("MATCH ()-[r:VIAJO_CON]->() DELETE r")
    coincidencias_antes = grafo_repo.coincidencias(min_viajes=1)
    assert len(coincidencias_antes) == 0

    # Reconciliar
    stats = reconciliacion_service.sync_neo4j_desde_mongo()
    assert stats["pares_reconstruidos"] == 2

    # Verificar que las aristas están de nuevo
    coincidencias_despues = grafo_repo.coincidencias(min_viajes=1)
    assert len(coincidencias_despues) == 2
    cantidades = sorted(c["viajes"] for c in coincidencias_despues)
    assert cantidades == [1, 3]


def test_sync_sin_viajes_devuelve_cero(mongo_clean, neo4j_clean):
    from src.services import reconciliacion_service
    stats = reconciliacion_service.sync_neo4j_desde_mongo()
    assert stats["pares_reconstruidos"] == 0


def test_procesar_outbox_cuenta_pendientes(tmp_path, monkeypatch):
    from src.utils import outbox
    from src.services import reconciliacion_service

    monkeypatch.setattr(outbox, "_OUTBOX_FILE", tmp_path / "outbox.log")
    outbox.enqueue("op1")
    outbox.enqueue("op2")
    stats = reconciliacion_service.procesar_outbox()
    assert stats["pendientes"] == 2


# --- Test extra (NO esta en el plan): verifica el rebuild Mongo->Neo4j sin depender
# --- de auth/vehiculo/viaje_service, insertando viajes finalizados directo en Mongo.
def test_sync_reconstruye_aristas_desde_mongo_directo(mongo_clean, neo4j_clean):
    from src.db.mongo import get_db
    from src.services import reconciliacion_service
    from src.repositories import grafo_repo

    get_db().viajes.insert_many([
        {"estado": "FINALIZADO", "usuario_id": "U1", "conductor_id": "C1"},
        {"estado": "FINALIZADO", "usuario_id": "U1", "conductor_id": "C1"},
        {"estado": "FINALIZADO", "usuario_id": "U1", "conductor_id": "C1"},
        {"estado": "FINALIZADO", "usuario_id": "U2", "conductor_id": "C1"},
        {"estado": "EN_CURSO",   "usuario_id": "U3", "conductor_id": "C1"},  # ignorado: no FINALIZADO
    ])

    stats = reconciliacion_service.sync_neo4j_desde_mongo()
    assert stats["pares_reconstruidos"] == 2
    assert stats["viajes_procesados"] == 4

    cantidades = sorted(c["viajes"] for c in grafo_repo.coincidencias(min_viajes=1))
    assert cantidades == [1, 3]
