"""Tests del vehiculo_repo (Postgres)."""
import uuid

import pytest


def _crear_conductor():
    # email y licencia unicos por llamada: en `conductor` ambos son UNIQUE,
    # y este helper se invoca varias veces dentro de un mismo test.
    u = uuid.uuid4().hex[:12]
    from src.repositories import conductor_repo
    return conductor_repo.crear(f"cond-{u}@mail.com", "h", "Conductor Test", f"LIC-{u}")


def test_crear_devuelve_id(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vid = vehiculo_repo.crear(cid, "ABC123D", "Toyota", "Corolla", 2020, "azul", "sedan")
    assert vid is not None and len(vid) == 36


def test_crear_sin_conductor_lanza_error(postgres_clean):
    from src.repositories import vehiculo_repo
    import psycopg
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        vehiculo_repo.crear("00000000-0000-0000-0000-000000000000", "XYZ", "Marca", "Modelo")


def test_crear_placa_duplicada_lanza_error(postgres_clean):
    from src.repositories import vehiculo_repo
    import psycopg
    cid = _crear_conductor()
    vehiculo_repo.crear(cid, "DUP123", "M", "M1")
    with pytest.raises(psycopg.errors.UniqueViolation):
        vehiculo_repo.crear(cid, "DUP123", "M", "M2")


def test_get_by_id(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vid = vehiculo_repo.crear(cid, "PLT001", "Honda", "Civic", 2021)
    v = vehiculo_repo.get_by_id(vid)
    assert v["placa"] == "PLT001"
    assert v["marca"] == "Honda"
    assert v["anio"] == 2021


def test_get_by_placa(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vehiculo_repo.crear(cid, "BUSCAR1", "M", "M")
    v = vehiculo_repo.get_by_placa("BUSCAR1")
    assert v is not None
    assert v["placa"] == "BUSCAR1"


def test_get_by_placa_no_existente(postgres_clean):
    from src.repositories import vehiculo_repo
    assert vehiculo_repo.get_by_placa("NOEXISTE") is None


def test_listar_por_conductor(postgres_clean):
    from src.repositories import vehiculo_repo
    cid_a = _crear_conductor()
    cid_b = _crear_conductor()
    vehiculo_repo.crear(cid_a, "A1", "M", "M")
    vehiculo_repo.crear(cid_a, "A2", "M", "M")
    vehiculo_repo.crear(cid_b, "B1", "M", "M")
    vehiculos_a = vehiculo_repo.listar_por_conductor(cid_a)
    assert len(vehiculos_a) == 2
    assert all(v["conductor_id"] == cid_a for v in vehiculos_a)


def test_existe(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vid = vehiculo_repo.crear(cid, "EXISTE", "M", "M")
    assert vehiculo_repo.existe(vid) is True
    assert vehiculo_repo.existe("00000000-0000-0000-0000-000000000000") is False
