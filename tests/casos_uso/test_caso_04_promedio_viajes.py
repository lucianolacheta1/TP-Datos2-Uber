"""Tests del caso de uso 4: tiempo promedio de viajes (Cassandra + Redis cache)."""
import pytest
import uuid
from datetime import date


def test_promedio_calculado_correctamente(cassandra_clean, redis_clean):
    from src.repositories import actividad_repo
    from src.casos_uso import caso_04_promedio_viajes

    hoy = date.today()
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 10, 5.0)
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 30, 10.0)
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 50, 15.0)

    assert caso_04_promedio_viajes.ejecutar() == pytest.approx(30)


def test_cachea_resultado(cassandra_clean, redis_clean):
    from src.repositories import actividad_repo, cache_repo
    from src.casos_uso import caso_04_promedio_viajes

    actividad_repo.insertar_viaje_finalizado(date.today(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 20, 5.0)
    caso_04_promedio_viajes.ejecutar()
    assert cache_repo.get_cache("viajes_promedio") == 20


def test_segunda_llamada_usa_cache(cassandra_clean, redis_clean):
    from src.repositories import cache_repo
    from src.casos_uso import caso_04_promedio_viajes

    cache_repo.set_cache("viajes_promedio", 99.5)
    assert caso_04_promedio_viajes.ejecutar() == 99.5


def test_sin_viajes_devuelve_cero(cassandra_clean, redis_clean):
    from src.casos_uso import caso_04_promedio_viajes
    assert caso_04_promedio_viajes.ejecutar() == 0
