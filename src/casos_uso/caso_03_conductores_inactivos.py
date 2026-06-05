"""Caso de uso 3: conductores inactivos en los últimos 30 días.

Inactivo = conductor activo en Postgres que NO tiene viaje finalizado
en los últimos 30 días (Cassandra).
"""
from datetime import datetime, UTC, timedelta

from src.repositories import actividad_repo, conductor_repo


DIAS_INACTIVIDAD = 30


def ejecutar() -> list[dict]:
    """Devuelve la lista de conductores activos que no tuvieron viajes recientes."""
    limite = datetime.now(UTC) - timedelta(days=DIAS_INACTIVIDAD)
    ids_con_actividad_reciente = set(
        str(cid) for cid in actividad_repo.conductores_activos_desde(limite)
    )

    todos_activos = conductor_repo.listar_activos()
    inactivos = [c for c in todos_activos if c["id"] not in ids_con_actividad_reciente]
    return inactivos
