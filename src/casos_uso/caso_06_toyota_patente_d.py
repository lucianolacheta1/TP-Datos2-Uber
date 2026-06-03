"""Caso de uso 6: cantidad de autos de cierta marca con patente terminada en X.

Por defecto: Toyota con patente terminada en "D".
Base: Neo4j (nodos Vehiculo).
"""
from src.repositories import grafo_repo


def ejecutar(marca: str = "Toyota", sufijo: str = "D") -> int:
    """Devuelve la cantidad de vehículos que cumplen ambos filtros."""
    return grafo_repo.vehiculos_marca_y_patente_termina(marca, sufijo)
