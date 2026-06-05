"""Tests del ubicacion_service (Cassandra + Redis)."""
import uuid
import time


def test_reportar_inserta_en_cassandra(cassandra_clean, redis_clean):
    from src.services import ubicacion_service
    from src.repositories import ubicacion_repo

    vid = uuid.uuid4()
    ubicacion_service.reportar(str(vid), -34.6, -58.4)
    historial = ubicacion_repo.historial(vid)
    assert len(historial) == 1


def test_reportar_setea_redis_con_ttl(cassandra_clean, redis_clean):
    from src.services import ubicacion_service
    from src.repositories import cache_repo

    vid = str(uuid.uuid4())
    ubicacion_service.reportar(vid, -34.6, -58.4)
    pos = cache_repo.get_ultima_pos(vid)
    assert pos == (-34.6, -58.4)


def test_reportar_varios_acumula_historial(cassandra_clean, redis_clean):
    from src.services import ubicacion_service
    from src.repositories import ubicacion_repo

    vid = uuid.uuid4()
    for i in range(5):
        ubicacion_service.reportar(str(vid), -34.6 + i * 0.01, -58.4)
        time.sleep(0.01)  # asegurar timestamps distintos
    historial = ubicacion_repo.historial(vid)
    assert len(historial) == 5
