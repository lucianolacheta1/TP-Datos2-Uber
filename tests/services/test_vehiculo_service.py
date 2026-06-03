"""Tests del vehiculo_service (Postgres + Neo4j).

Nota: el plan original arma el conductor de prueba con `auth_service.register_conductor`.
Como `auth_service` todavía no existe (otro dueño), acá se arma la precondición
directamente: conductor en Postgres (`conductor_repo`) + nodo Conductor en Neo4j
(`grafo_repo.crear_conductor`) — que es exactamente lo que proyectaría auth_service.
Cuando exista auth_service se puede reemplazar el helper sin tocar los asserts.
"""
import uuid

import pytest


def _crear_conductor(nombre="Conductor Test"):
    from src.repositories import conductor_repo, grafo_repo
    u = uuid.uuid4().hex[:12]
    email = f"cond-{u}@mail.com"
    cid = conductor_repo.crear(email, "h", nombre, f"LIC-{u}")
    grafo_repo.crear_conductor(cid, nombre, email)  # proyección que normalmente hace auth_service
    return cid


def test_registrar_persiste_en_postgres(postgres_clean, neo4j_clean):
    from src.services import vehiculo_service
    from src.repositories import vehiculo_repo

    cid = _crear_conductor()
    vid = vehiculo_service.registrar(cid, "ABC123D", "Toyota", "Corolla", 2020)
    v = vehiculo_repo.get_by_id(vid)
    assert v is not None
    assert v["placa"] == "ABC123D"


def test_registrar_crea_nodo_y_relacion_en_neo4j(postgres_clean, neo4j_clean):
    from src.services import vehiculo_service
    from src.db.neo4j_db import get_driver

    cid = _crear_conductor()
    vid = vehiculo_service.registrar(cid, "XYZ999D", "Toyota", "Hilux", 2021)
    with get_driver().session() as s:
        rel = s.run(
            """MATCH (c:Conductor {id:$cid})-[r:MANEJA]->(v:Vehiculo {id:$vid})
               RETURN v.placa AS placa, v.marca AS marca""",
            cid=cid, vid=vid,
        ).single()
        assert rel is not None
        assert rel["placa"] == "XYZ999D"
        assert rel["marca"] == "Toyota"


def test_registrar_con_conductor_inexistente_lanza_error(postgres_clean, neo4j_clean):
    from src.services import vehiculo_service
    from src.utils.errors import ConductorInexistente

    with pytest.raises(ConductorInexistente):
        vehiculo_service.registrar(
            "00000000-0000-0000-0000-000000000000",
            "ABC", "M", "M"
        )
