"""Tests del actividad_repo (Cassandra)."""
import pytest
import uuid
from datetime import datetime, UTC, timedelta, date


def test_upsert_ultima_inserta(cassandra_clean):
    from src.repositories import actividad_repo
    cid = uuid.uuid4()
    vid = uuid.uuid4()
    ts = datetime.now(UTC)
    actividad_repo.upsert_ultima(cid, ts, vid)
    ultima = actividad_repo.get_ultima(cid)
    assert ultima is not None
    assert ultima["ultimo_viaje_id"] == vid


def test_upsert_ultima_sobrescribe(cassandra_clean):
    from src.repositories import actividad_repo
    cid = uuid.uuid4()
    v1, v2 = uuid.uuid4(), uuid.uuid4()
    ts1 = datetime.now(UTC)
    ts2 = ts1 + timedelta(hours=1)
    actividad_repo.upsert_ultima(cid, ts1, v1)
    actividad_repo.upsert_ultima(cid, ts2, v2)
    ultima = actividad_repo.get_ultima(cid)
    assert ultima["ultimo_viaje_id"] == v2


def test_get_ultima_no_existente(cassandra_clean):
    from src.repositories import actividad_repo
    assert actividad_repo.get_ultima(uuid.uuid4()) is None


def test_conductores_activos_desde(cassandra_clean):
    from src.repositories import actividad_repo
    activo = uuid.uuid4()
    inactivo = uuid.uuid4()
    ahora = datetime.now(UTC)
    actividad_repo.upsert_ultima(activo, ahora, uuid.uuid4())
    actividad_repo.upsert_ultima(inactivo, ahora - timedelta(days=60), uuid.uuid4())
    activos = actividad_repo.conductores_activos_desde(ahora - timedelta(days=30))
    assert activo in activos
    assert inactivo not in activos


def test_insertar_viaje_finalizado_y_promedio(cassandra_clean):
    from src.repositories import actividad_repo
    hoy = date.today()
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 20, 5.0)
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 40, 10.0)
    promedio = actividad_repo.promedio_duracion()
    assert promedio == pytest.approx(30)


def test_promedio_sin_viajes(cassandra_clean):
    from src.repositories import actividad_repo
    assert actividad_repo.promedio_duracion() == 0
