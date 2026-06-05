"""Repository de actividad (Cassandra).

Mantiene ultima_actividad_conductor (para caso 3) y
viajes_finalizados_por_dia (para caso 4).
"""
from datetime import datetime, date
from uuid import UUID
from src.db.cassandra import get_session


def upsert_ultima(conductor_id: UUID, ts: datetime, viaje_id: UUID) -> None:
    """Inserta o actualiza la última actividad del conductor."""
    cql = """
        INSERT INTO ultima_actividad_conductor
            (conductor_id, ultimo_viaje_ts, ultimo_viaje_id)
        VALUES (%s, %s, %s)
    """
    get_session().execute(cql, (conductor_id, ts, viaje_id))


def get_ultima(conductor_id: UUID) -> dict | None:
    cql = """
        SELECT conductor_id, ultimo_viaje_ts, ultimo_viaje_id
        FROM ultima_actividad_conductor WHERE conductor_id = %s
    """
    row = get_session().execute(cql, (conductor_id,)).one()
    if row is None:
        return None
    return {
        "conductor_id": row.conductor_id,
        "ultimo_viaje_ts": row.ultimo_viaje_ts,
        "ultimo_viaje_id": row.ultimo_viaje_id,
    }


def conductores_activos_desde(fecha_limite: datetime) -> list[UUID]:
    """Devuelve los conductor_ids con ultimo_viaje_ts >= fecha_limite.

    OJO: usa ALLOW FILTERING porque no hay índice secundario en ultimo_viaje_ts.
    Para el TP es aceptable; en producción se usaría una tabla denormalizada.
    """
    cql = """
        SELECT conductor_id, ultimo_viaje_ts
        FROM ultima_actividad_conductor
        WHERE ultimo_viaje_ts >= %s
        ALLOW FILTERING
    """
    rows = get_session().execute(cql, (fecha_limite,))
    return [r.conductor_id for r in rows]


def insertar_viaje_finalizado(dia: date, viaje_id: UUID, conductor_id: UUID,
                              usuario_id: UUID, duracion_min: int,
                              distancia_km: float) -> None:
    cql = """
        INSERT INTO viajes_finalizados_por_dia
            (dia, viaje_id, conductor_id, usuario_id, duracion_min, distancia_km)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    get_session().execute(cql, (dia, viaje_id, conductor_id, usuario_id,
                                duracion_min, distancia_km))


def promedio_duracion() -> float:
    """Caso de uso 4: tiempo promedio de viajes finalizados.

    Cassandra no tiene AVG nativo eficiente; se calcula en app
    (recorrido completo, OK para el volumen de un TP).
    """
    cql = "SELECT duracion_min FROM viajes_finalizados_por_dia"
    rows = list(get_session().execute(cql))
    if not rows:
        return 0
    total = sum(r.duracion_min for r in rows)
    return total / len(rows)
