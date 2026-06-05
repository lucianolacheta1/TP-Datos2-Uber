"""Pago service: procesar pagos asociados a viajes finalizados.

Toca:
- Mongo → viajes (lectura para validar) + pagos (escritura).
"""
from datetime import datetime, UTC

from src.repositories import viaje_repo, pago_repo
from src.utils.errors import ViajeNoEncontrado


def procesar(viaje_id: str,
             monto_total: float,
             tarifa_base: float,
             tarifa_distancia: float,
             tarifa_tiempo: float,
             cargos_extra: float,
             metodo_pago: str) -> str:
    """Procesa un pago para un viaje. Estado siempre APROBADO en el TP."""
    if viaje_repo.get_by_id(viaje_id) is None:
        raise ViajeNoEncontrado(viaje_id)

    pago_doc = {
        "viaje_id":         viaje_id,
        "monto_total":      monto_total,
        "tarifa_base":      tarifa_base,
        "tarifa_distancia": tarifa_distancia,
        "tarifa_tiempo":    tarifa_tiempo,
        "cargos_extra":     cargos_extra,
        "metodo_pago":      metodo_pago,
        "estado":           "APROBADO",
        "timestamp":        datetime.now(UTC),
    }
    return pago_repo.crear(pago_doc)
