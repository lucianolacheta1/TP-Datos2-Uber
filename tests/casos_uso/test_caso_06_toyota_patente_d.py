"""Tests del caso de uso 6: Toyota patente terminada en D (Neo4j)."""


def test_cuenta_solo_toyota_con_patente_terminada_en_D(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_06_toyota_patente_d

    grafo_repo.crear_vehiculo("V1", "ABC123D", "Toyota", "Corolla")
    grafo_repo.crear_vehiculo("V2", "XYZ888D", "Toyota", "Hilux")
    grafo_repo.crear_vehiculo("V3", "AAA111A", "Toyota", "Etios")     # no termina en D
    grafo_repo.crear_vehiculo("V4", "BBB222D", "Honda", "Civic")      # no Toyota

    assert caso_06_toyota_patente_d.ejecutar() == 2


def test_acepta_parametros_marca_y_sufijo(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_06_toyota_patente_d

    grafo_repo.crear_vehiculo("V1", "AAA111A", "Honda", "Civic")
    grafo_repo.crear_vehiculo("V2", "BBB222A", "Honda", "Fit")
    assert caso_06_toyota_patente_d.ejecutar(marca="Honda", sufijo="A") == 2


def test_sin_vehiculos_devuelve_cero(neo4j_clean):
    from src.casos_uso import caso_06_toyota_patente_d
    assert caso_06_toyota_patente_d.ejecutar() == 0
