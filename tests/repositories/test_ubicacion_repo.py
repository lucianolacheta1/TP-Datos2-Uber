"""Tests del ubicacion_repo (Cassandra)."""
import uuid
from datetime import datetime, UTC, timedelta

import pytest


def test_insertar_sin_error(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    ubicacion_repo.insertar(vid, datetime.now(UTC), -34.6, -58.4)
    # Sin error → OK


def test_historial_devuelve_inserts(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    base_ts = datetime.now(UTC)
    for i in range(5):
        ubicacion_repo.insertar(vid, base_ts + timedelta(seconds=i), -34.6 + i * 0.001, -58.4)
    historial = ubicacion_repo.historial(vid)
    assert len(historial) == 5


def test_historial_orden_descendente(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    base_ts = datetime.now(UTC)
    for i in range(3):
        ubicacion_repo.insertar(vid, base_ts + timedelta(seconds=i), -34.6, -58.4)
    historial = ubicacion_repo.historial(vid)
    # CLUSTERING ORDER BY (ts DESC) → primero el más reciente
    assert historial[0]["ts"] > historial[-1]["ts"]


def test_historial_vehiculo_sin_ubicaciones(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    assert ubicacion_repo.historial(vid) == []


def test_ultima_posicion_devuelve_la_mas_reciente(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    base_ts = datetime.now(UTC)
    ubicacion_repo.insertar(vid, base_ts, -34.6, -58.4)
    ubicacion_repo.insertar(vid, base_ts + timedelta(seconds=10), -34.7, -58.5)
    ultima = ubicacion_repo.ultima_posicion(vid)
    assert ultima is not None
    assert float(ultima["lat"]) == pytest.approx(-34.7)


def test_ultima_posicion_sin_datos(cassandra_clean):
    from src.repositories import ubicacion_repo
    assert ubicacion_repo.ultima_posicion(uuid.uuid4()) is None
