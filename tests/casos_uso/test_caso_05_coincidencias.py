"""Tests del caso de uso 5: coincidencias usuario-conductor (Neo4j)."""


def test_devuelve_parejas_con_mas_de_1_viaje(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_05_coincidencias

    # Crear nodos
    grafo_repo.crear_usuario("U1", "U1", "u1@m.com")
    grafo_repo.crear_usuario("U2", "U2", "u2@m.com")
    grafo_repo.crear_conductor("C1", "C1", "c1@m.com")
    grafo_repo.crear_conductor("C2", "C2", "c2@m.com")

    # U1-C1: 3 viajes
    for _ in range(3):
        grafo_repo.incrementar_viajo_con("U1", "C1")
    # U2-C2: 1 viaje (NO debe aparecer)
    grafo_repo.incrementar_viajo_con("U2", "C2")

    coincidencias = caso_05_coincidencias.ejecutar()
    pares = {(c["pasajero_id"], c["conductor_id"]) for c in coincidencias}
    assert ("U1", "C1") in pares
    assert ("U2", "C2") not in pares


def test_acepta_min_viajes_parametro(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_05_coincidencias

    grafo_repo.crear_usuario("U", "U", "u@m.com")
    grafo_repo.crear_conductor("C", "C", "c@m.com")
    for _ in range(5):
        grafo_repo.incrementar_viajo_con("U", "C")

    assert len(caso_05_coincidencias.ejecutar(min_viajes=3)) == 1
    assert len(caso_05_coincidencias.ejecutar(min_viajes=10)) == 0


def test_sin_aristas_devuelve_lista_vacia(neo4j_clean):
    from src.casos_uso import caso_05_coincidencias
    assert caso_05_coincidencias.ejecutar() == []
