"""Tests del pago_service (Mongo)."""
import pytest


def _setup_viaje_finalizado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import auth_service, vehiculo_service, viaje_service
    uid = auth_service.register_usuario("u@m.com", "p", "U")
    cid = auth_service.register_conductor("c@m.com", "p", "C", "L1")
    vid = vehiculo_service.registrar(cid, "P1", "M", "M")
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 15)
    return viaje_id


def test_procesar_inserta_pago_en_mongo(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import pago_service
    from src.repositories import pago_repo

    viaje_id = _setup_viaje_finalizado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    pago_id = pago_service.procesar(
        viaje_id, monto_total=2500, tarifa_base=500,
        tarifa_distancia=1200, tarifa_tiempo=600,
        cargos_extra=200, metodo_pago="TARJETA",
    )
    p = pago_repo.get_by_id(pago_id)
    assert p["monto_total"] == 2500
    assert p["metodo_pago"] == "TARJETA"
    assert p["viaje_id"] == viaje_id


def test_procesar_estado_aprobado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import pago_service
    from src.repositories import pago_repo

    viaje_id = _setup_viaje_finalizado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    pago_id = pago_service.procesar(viaje_id, 1000, 500, 300, 200, 0, "EFECTIVO")
    p = pago_repo.get_by_id(pago_id)
    assert p["estado"] == "APROBADO"


def test_procesar_viaje_inexistente_lanza_error(mongo_clean):
    from src.services import pago_service
    from src.utils.errors import ViajeNoEncontrado

    with pytest.raises(ViajeNoEncontrado):
        pago_service.procesar(
            "507f1f77bcf86cd799439011",
            1000, 500, 300, 200, 0, "TARJETA",
        )
