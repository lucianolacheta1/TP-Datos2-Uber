"""Vehiculo service: registro con proyección al grafo.

Toca:
- Postgres → vehiculo (SOT).
- Neo4j   → nodo (:Vehiculo) + relación [:MANEJA] desde el Conductor (best-effort).
"""
from src.repositories import conductor_repo, vehiculo_repo, grafo_repo
from src.utils import outbox
from src.utils.errors import ConductorInexistente
from src.utils.logger import logger


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


def registrar(conductor_id: str, placa: str, marca: str, modelo: str,
              anio: int | None = None, color: str | None = None,
              tipo: str | None = None) -> str:
    """Registra un vehiculo en Postgres y proyecta al grafo."""
    if not conductor_repo.existe(conductor_id):
        raise ConductorInexistente(conductor_id)

    vehiculo_id = vehiculo_repo.crear(conductor_id, placa, marca, modelo, anio, color, tipo)

    _intentar("neo4j_crear_vehiculo",
              lambda: grafo_repo.crear_vehiculo(vehiculo_id, placa, marca, modelo, anio))
    _intentar("neo4j_relacion_maneja",
              lambda: grafo_repo.crear_relacion_maneja(conductor_id, vehiculo_id))

    return vehiculo_id
