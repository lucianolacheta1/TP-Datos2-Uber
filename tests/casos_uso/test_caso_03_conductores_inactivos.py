"""Tests del caso de uso 3: conductores inactivos último mes (Cassandra + Postgres)."""
import uuid
from datetime import datetime, UTC, timedelta


def test_inactivo_es_quien_no_tuvo_viajes_en_30_dias(postgres_clean, cassandra_clean):
    from src.repositories import conductor_repo, actividad_repo
    from src.casos_uso import caso_03_conductores_inactivos

    activo_id = conductor_repo.crear("a@m.com", "h", "Activo", "LIC-A")
    inactivo_id = conductor_repo.crear("i@m.com", "h", "Inactivo", "LIC-I")
    nunca_id = conductor_repo.crear("n@m.com", "h", "Nunca", "LIC-N")

    ahora = datetime.now(UTC)
    actividad_repo.upsert_ultima(uuid.UUID(activo_id), ahora, uuid.uuid4())
    actividad_repo.upsert_ultima(uuid.UUID(inactivo_id), ahora - timedelta(days=60), uuid.uuid4())
    # nunca_id no tiene actividad

    inactivos = caso_03_conductores_inactivos.ejecutar()
    ids = [c["id"] for c in inactivos]
    assert activo_id not in ids
    assert inactivo_id in ids
    assert nunca_id in ids


def test_sin_conductores_devuelve_lista_vacia(postgres_clean, cassandra_clean):
    from src.casos_uso import caso_03_conductores_inactivos
    assert caso_03_conductores_inactivos.ejecutar() == []
