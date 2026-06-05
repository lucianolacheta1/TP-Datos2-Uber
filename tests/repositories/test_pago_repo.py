"""Tests del pago_repo (Mongo)."""
from datetime import datetime, UTC


def _pago_template(viaje_id="v1", metodo="TARJETA", monto=2500):
    return {
        "viaje_id": viaje_id,
        "monto_total": monto,
        "tarifa_base": 500,
        "tarifa_distancia": 1200,
        "tarifa_tiempo": 600,
        "cargos_extra": monto - 2300,
        "metodo_pago": metodo,
        "estado": "APROBADO",
        "timestamp": datetime.now(UTC),
    }


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import pago_repo
    pid = pago_repo.crear(_pago_template())
    assert pid is not None and len(pid) == 24


def test_get_by_id(mongo_clean):
    from src.repositories import pago_repo
    pid = pago_repo.crear(_pago_template(monto=3000))
    p = pago_repo.get_by_id(pid)
    assert p["monto_total"] == 3000


def test_get_by_viaje_id(mongo_clean):
    from src.repositories import pago_repo
    pago_repo.crear(_pago_template(viaje_id="VIAJE-X"))
    p = pago_repo.get_by_viaje_id("VIAJE-X")
    assert p is not None
    assert p["viaje_id"] == "VIAJE-X"


def test_get_by_viaje_id_no_existente(mongo_clean):
    from src.repositories import pago_repo
    assert pago_repo.get_by_viaje_id("NO-EXISTE") is None


def test_contar_por_metodo(mongo_clean):
    from src.repositories import pago_repo
    for _ in range(3):
        pago_repo.crear(_pago_template(metodo="TARJETA"))
    for _ in range(2):
        pago_repo.crear(_pago_template(metodo="EFECTIVO"))
    pago_repo.crear(_pago_template(metodo="BILLETERA_VIRTUAL"))
    counts = pago_repo.contar_por_metodo()
    assert counts == {"TARJETA": 3, "EFECTIVO": 2, "BILLETERA_VIRTUAL": 1}


def test_metodo_menos_usado(mongo_clean):
    from src.repositories import pago_repo
    for _ in range(3):
        pago_repo.crear(_pago_template(metodo="TARJETA"))
    pago_repo.crear(_pago_template(metodo="EFECTIVO"))
    assert pago_repo.metodo_menos_usado() == "EFECTIVO"


def test_metodo_menos_usado_sin_pagos(mongo_clean):
    from src.repositories import pago_repo
    assert pago_repo.metodo_menos_usado() is None
