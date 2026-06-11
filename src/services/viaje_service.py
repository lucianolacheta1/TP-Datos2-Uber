"""Viaje service: solicitar, iniciar, finalizar.

Toca:
- Postgres → lectura de usuario/conductor para snapshots.
- Mongo    → viajes (SOT).
- Cassandra → ultima_actividad_conductor + viajes_finalizados_por_dia (proyección).
- Neo4j    → incremento de arista VIAJO_CON (proyección).
- Redis    → invalidación de cache de queries pesadas (proyección).
"""
import uuid
from datetime import datetime, UTC, date

from src.repositories import (
    usuario_repo, conductor_repo, vehiculo_repo,
    viaje_repo, actividad_repo, grafo_repo, cache_repo,
)
from src.utils import outbox
from src.utils.errors import (
    UsuarioInexistente, ConductorInexistente,
    VehiculoInexistente, ViajeNoEncontrado, EstadoInvalido,
)
from src.utils.logger import logger


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


def _viaje_id_a_uuid(viaje_id: str) -> uuid.UUID:
    """El _id de un viaje es un ObjectId de Mongo (24 hex), pero las tablas
    de Cassandra usan columnas UUID. Lo convertimos de forma determinística
    rellenando con ceros a la izquierda hasta 32 hex (reversible y estable)."""
    return uuid.UUID(viaje_id.rjust(32, "0"))


# ----------------- solicitar -----------------

def solicitar(usuario_id: str, conductor_id: str, vehiculo_id: str,
              origen: dict, destino: dict) -> str:
    """Crea un viaje en estado PENDIENTE en Mongo con snapshots de Postgres."""
    usuario = usuario_repo.get_by_id(usuario_id)
    if usuario is None:
        raise UsuarioInexistente(usuario_id)
    conductor = conductor_repo.get_by_id(conductor_id)
    if conductor is None:
        raise ConductorInexistente(conductor_id)
    if not vehiculo_repo.existe(vehiculo_id):
        raise VehiculoInexistente(vehiculo_id)

    doc = {
        "usuario_id":   usuario_id,
        "conductor_id": conductor_id,
        "vehiculo_id":  vehiculo_id,
        "origen":  origen,
        "destino": destino,
        "estado":  "PENDIENTE",
        "ts_solicitud": datetime.now(UTC),
        "usuario_snapshot": {
            "nombre": usuario["nombre"],
            "rating": usuario["rating_promedio"],
        },
        "conductor_snapshot": {
            "nombre": conductor["nombre"],
            "rating": conductor["rating_promedio"],
        },
    }
    return viaje_repo.crear(doc)


# ----------------- lecturas para el menu -----------------
# El menu no puede llamar a repositories directamente (regla de capas),
# por eso el service expone estos listados de solo lectura.

def obtener(viaje_id: str) -> dict | None:
    """Devuelve el viaje por id, o None si no existe."""
    return viaje_repo.get_by_id(viaje_id)


def listar_de_conductor(conductor_id: str, estado: str) -> list[dict]:
    """Viajes de un conductor filtrados por estado."""
    return viaje_repo.listar_por_conductor(conductor_id, estado)


def listar_de_usuario(usuario_id: str, estado: str) -> list[dict]:
    """Viajes de un usuario filtrados por estado."""
    return viaje_repo.listar_por_usuario(usuario_id, estado)


# ----------------- iniciar -----------------

def iniciar(viaje_id: str) -> bool:
    """Transición PENDIENTE → EN_CURSO."""
    return viaje_repo.iniciar(viaje_id)


# ----------------- finalizar -----------------

def finalizar(viaje_id: str, distancia_km: float, duracion_min: int) -> None:
    """Transición EN_CURSO → FINALIZADO + proyecciones a Cassandra/Neo4j/Redis."""
    ok = viaje_repo.finalizar(viaje_id, distancia_km, duracion_min)
    if not ok:
        # O no existe o no estaba EN_CURSO
        viaje = viaje_repo.get_by_id(viaje_id)
        if viaje is None:
            raise ViajeNoEncontrado(viaje_id)
        raise EstadoInvalido(f"Viaje {viaje_id} no está EN_CURSO")

    viaje = viaje_repo.get_by_id(viaje_id)
    cid_uuid = uuid.UUID(viaje["conductor_id"])
    uid_uuid = uuid.UUID(viaje["usuario_id"])
    vid_uuid = _viaje_id_a_uuid(viaje_id)
    ts_fin = viaje["ts_fin"]
    if ts_fin.tzinfo is None:
        ts_fin = ts_fin.replace(tzinfo=UTC)

    # Proyección 1: última actividad del conductor (Cassandra)
    _intentar(
        "cassandra_ultima_actividad",
        lambda: actividad_repo.upsert_ultima(cid_uuid, ts_fin, vid_uuid),
    )

    # Proyección 2: viajes finalizados por día (Cassandra)
    _intentar(
        "cassandra_viajes_finalizados",
        lambda: actividad_repo.insertar_viaje_finalizado(
            ts_fin.date(), vid_uuid, cid_uuid, uid_uuid, duracion_min, distancia_km
        ),
    )

    # Proyección 3: arista VIAJO_CON en Neo4j
    _intentar(
        "neo4j_arista_viajo_con",
        lambda: grafo_repo.incrementar_viajo_con(viaje["usuario_id"], viaje["conductor_id"]),
    )

    # Proyección 4: invalidación de caches relacionados
    _intentar("redis_invalidar_viajes_promedio",
              lambda: cache_repo.invalidar("viajes_promedio"))
