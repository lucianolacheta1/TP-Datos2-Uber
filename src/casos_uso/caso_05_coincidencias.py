"""Caso de uso 5: pasajeros y conductores que coincidieron en >1 viaje.

Base: Neo4j (relación VIAJO_CON con propiedad cantidad_viajes).
"""
from src.repositories import grafo_repo


def ejecutar(min_viajes: int = 2) -> list[dict]:
    """Devuelve parejas (pasajero, conductor) que coincidieron en N o más viajes.

    Formato: [{pasajero_id, pasajero, conductor_id, conductor, viajes}, ...]
    """
    return grafo_repo.coincidencias(min_viajes=min_viajes)
