"""Repository de Ubicacion (Cassandra). Time-series de posiciones GPS."""
from datetime import datetime
from uuid import UUID
from src.db.cassandra import get_session


def insertar(vehiculo_id: UUID, ts: datetime, lat: float, lon: float,
             precision_m: float | None = None, viaje_id: UUID | None = None) -> None:
    """Inserta una nueva posición GPS."""
    cql = """
        INSERT INTO ubicaciones_por_vehiculo
            (vehiculo_id, ts, lat, lon, precision_m, viaje_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    get_session().execute(cql, (vehiculo_id, ts, lat, lon, precision_m, viaje_id))


def historial(vehiculo_id: UUID, limit: int = 100) -> list[dict]:
    """Devuelve el historial GPS de un vehículo, más reciente primero."""
    cql = """
        SELECT vehiculo_id, ts, lat, lon, precision_m, viaje_id
        FROM ubicaciones_por_vehiculo
        WHERE vehiculo_id = %s
        LIMIT %s
    """
    rows = get_session().execute(cql, (vehiculo_id, limit))
    return [
        {
            "vehiculo_id": r.vehiculo_id, "ts": r.ts,
            "lat": r.lat, "lon": r.lon,
            "precision_m": r.precision_m, "viaje_id": r.viaje_id,
        }
        for r in rows
    ]


def ultima_posicion(vehiculo_id: UUID) -> dict | None:
    """Devuelve la posición más reciente o None."""
    cql = """
        SELECT vehiculo_id, ts, lat, lon, precision_m, viaje_id
        FROM ubicaciones_por_vehiculo
        WHERE vehiculo_id = %s LIMIT 1
    """
    row = get_session().execute(cql, (vehiculo_id,)).one()
    if row is None:
        return None
    return {
        "vehiculo_id": row.vehiculo_id, "ts": row.ts,
        "lat": row.lat, "lon": row.lon,
        "precision_m": row.precision_m, "viaje_id": row.viaje_id,
    }
