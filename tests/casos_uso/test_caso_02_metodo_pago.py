"""Tests del caso de uso 2: método de pago menos usado (Mongo)."""
from datetime import datetime, UTC


def _crear_pago(metodo: str):
    from src.repositories import pago_repo
    pago_repo.crear({
        "viaje_id": "v",
        "monto_total": 1000, "tarifa_base": 500,
        "tarifa_distancia": 300, "tarifa_tiempo": 200, "cargos_extra": 0,
        "metodo_pago": metodo, "estado": "APROBADO",
        "timestamp": datetime.now(UTC),
    })


def test_devuelve_metodo_con_menos_pagos(mongo_clean):
    from src.casos_uso import caso_02_metodo_pago

    for _ in range(5):
        _crear_pago("TARJETA")
    for _ in range(2):
        _crear_pago("EFECTIVO")
    _crear_pago("BILLETERA_VIRTUAL")
    assert caso_02_metodo_pago.ejecutar() == "BILLETERA_VIRTUAL"


def test_sin_pagos_devuelve_none(mongo_clean):
    from src.casos_uso import caso_02_metodo_pago
    assert caso_02_metodo_pago.ejecutar() is None
