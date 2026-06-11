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


def listar_conductores_disponibles() -> list[dict]:
    """Conductores ACTIVOS que tienen al menos un vehiculo registrado.

    Para que el menu ofrezca una eleccion por lista en vez de pedir IDs
    internos. Formato: [{"conductor": {...}, "vehiculos": [{...}, ...]}].
    """
    disponibles = []
    for conductor in conductor_repo.listar_activos():
        vehiculos = vehiculo_repo.listar_por_conductor(conductor["id"])
        if vehiculos:
            disponibles.append({"conductor": conductor, "vehiculos": vehiculos})
    return disponibles


def listar_de_conductor(conductor_id: str) -> list[dict]:
    """Vehiculos registrados de un conductor (para el menu)."""
    return vehiculo_repo.listar_por_conductor(conductor_id)


def listar_todos() -> list[dict]:
    """Todos los vehiculos registrados (para el menu admin)."""
    return vehiculo_repo.listar_todos()


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
