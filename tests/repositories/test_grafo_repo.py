"""Tests del grafo_repo (Neo4j)."""


def test_crear_usuario_y_existe(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_usuario("U1", "Juan", "j@m.com")
    with get_driver().session() as s:
        n = s.run("MATCH (u:Usuario {id:'U1'}) RETURN u").single()
        assert n is not None
        assert n["u"]["nombre"] == "Juan"


def test_crear_conductor_idempotente(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_conductor("C1", "Ana", "a@m.com", rating=4.5)
    # Crear de nuevo no debe duplicar (MERGE)
    grafo_repo.crear_conductor("C1", "Ana", "a@m.com", rating=4.5)
    with get_driver().session() as s:
        count = s.run("MATCH (c:Conductor {id:'C1'}) RETURN count(c) AS c").single()["c"]
        assert count == 1


def test_crear_vehiculo_con_relacion_maneja(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_conductor("C1", "Ana", "a@m.com")
    grafo_repo.crear_vehiculo("V1", "ABC123D", "Toyota", "Corolla", 2020)
    grafo_repo.crear_relacion_maneja("C1", "V1")
    with get_driver().session() as s:
        rel = s.run("MATCH (c:Conductor {id:'C1'})-[r:MANEJA]->(v:Vehiculo {id:'V1'}) RETURN r").single()
        assert rel is not None


def test_incrementar_viajo_con_primera_vez(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_usuario("U", "U", "u@m.com")
    grafo_repo.crear_conductor("C", "C", "c@m.com")
    grafo_repo.incrementar_viajo_con("U", "C")
    with get_driver().session() as s:
        rel = s.run("MATCH (:Usuario {id:'U'})-[r:VIAJO_CON]->(:Conductor {id:'C'}) RETURN r.cantidad_viajes AS n").single()
        assert rel["n"] == 1


def test_incrementar_viajo_con_repetido(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_usuario("U", "U", "u@m.com")
    grafo_repo.crear_conductor("C", "C", "c@m.com")
    for _ in range(3):
        grafo_repo.incrementar_viajo_con("U", "C")
    with get_driver().session() as s:
        rel = s.run("MATCH (:Usuario {id:'U'})-[r:VIAJO_CON]->(:Conductor {id:'C'}) RETURN r.cantidad_viajes AS n").single()
        assert rel["n"] == 3


def test_coincidencias_devuelve_solo_min_viajes(neo4j_clean):
    from src.repositories import grafo_repo
    grafo_repo.crear_usuario("U1", "U1", "u1@m.com")
    grafo_repo.crear_usuario("U2", "U2", "u2@m.com")
    grafo_repo.crear_conductor("C1", "C1", "c1@m.com")
    grafo_repo.crear_conductor("C2", "C2", "c2@m.com")
    # U1-C1: 3 viajes
    for _ in range(3):
        grafo_repo.incrementar_viajo_con("U1", "C1")
    # U2-C2: 1 viaje (no debe aparecer)
    grafo_repo.incrementar_viajo_con("U2", "C2")
    # U1-C2: 2 viajes
    for _ in range(2):
        grafo_repo.incrementar_viajo_con("U1", "C2")
    coincidencias = grafo_repo.coincidencias(min_viajes=2)
    assert len(coincidencias) == 2
    # U1-C1 debe estar (3 viajes) y U1-C2 (2 viajes)
    pares = {(c["pasajero_id"], c["conductor_id"]) for c in coincidencias}
    assert ("U1", "C1") in pares
    assert ("U1", "C2") in pares
    assert ("U2", "C2") not in pares


def test_vehiculos_marca_y_patente_termina(neo4j_clean):
    from src.repositories import grafo_repo
    grafo_repo.crear_vehiculo("V1", "ABC123D", "Toyota", "Corolla")
    grafo_repo.crear_vehiculo("V2", "XYZ999D", "Toyota", "Hilux")
    grafo_repo.crear_vehiculo("V3", "AAA111A", "Toyota", "Etios")  # no termina en D
    grafo_repo.crear_vehiculo("V4", "BBB222D", "Honda", "Civic")   # no Toyota
    cantidad = grafo_repo.vehiculos_marca_y_patente_termina("Toyota", "D")
    assert cantidad == 2
