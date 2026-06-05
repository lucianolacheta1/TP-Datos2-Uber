"""Ubicacion service: streaming GPS de vehiculos.

Toca:
- Cassandra → ubicaciones_por_vehiculo (histórico completo).
- Redis    → última posición con TTL corto (matching de viajes).
"""
import uuid
from datetime import datetime, UTC

from src.repositories import ubicacion_repo, cache_repo
from src.utils import outbox
from src.utils.logger import logger


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


def reportar(vehiculo_id: str, lat: float, lon: float,
             viaje_id: str | None = None) -> None:
    """Registra una posición GPS del vehículo en histórico y última posición."""
    vid_uuid = uuid.UUID(vehiculo_id)
    vj_uuid = uuid.UUID(viaje_id) if viaje_id else None
    ts = datetime.now(UTC)

    # 1. SOT: histórico en Cassandra
    ubicacion_repo.insertar(vid_uuid, ts, lat, lon, viaje_id=vj_uuid)

    # 2. Proyección: última posición en Redis (best-effort)
    _intentar("redis_ultima_pos",
              lambda: cache_repo.set_ultima_pos(vehiculo_id, lat, lon))
