"""Tests del viaje_repo (Mongo)."""
import pytest
from datetime import datetime, UTC


def _viaje_template(usuario_id="u1", conductor_id="c1", vehiculo_id="v1",
                    estado="PENDIENTE"):
    return {
        "usuario_id": usuario_id,
        "conductor_id": conductor_id,
        "vehiculo_id": vehiculo_id,
        "origen": {"lat": -34.6, "lon": -58.4, "direccion": "Palermo"},
        "destino": {"lat": -34.55, "lon": -58.45, "direccion": "Belgrano"},
        "estado": estado,
        "ts_solicitud": datetime.now(UTC),
        "usuario_snapshot": {"nombre": "Test User", "rating": 0},
        "conductor_snapshot": {"nombre": "Test Driver", "rating": 0},
    }


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template())
    assert vid is not None
    assert len(vid) == 24  # ObjectId hex string


def test_get_by_id_existente(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(usuario_id="UID-123"))
    v = viaje_repo.get_by_id(vid)
    assert v["usuario_id"] == "UID-123"


def test_get_by_id_no_existente(mongo_clean):
    from src.repositories import viaje_repo
    assert viaje_repo.get_by_id("507f1f77bcf86cd799439011") is None


def test_iniciar_viaje_pendiente(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="PENDIENTE"))
    ok = viaje_repo.iniciar(vid)
    assert ok is True
    assert viaje_repo.get_by_id(vid)["estado"] == "EN_CURSO"


def test_iniciar_viaje_ya_iniciado_falla(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="EN_CURSO"))
    ok = viaje_repo.iniciar(vid)
    assert ok is False


def test_finalizar_viaje_en_curso(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="EN_CURSO"))
    ok = viaje_repo.finalizar(vid, distancia_km=8.5, duracion_min=22)
    assert ok is True
    v = viaje_repo.get_by_id(vid)
    assert v["estado"] == "FINALIZADO"
    assert v["distancia_km"] == 8.5
    assert v["duracion_min"] == 22
    assert v["ts_fin"] is not None


def test_finalizar_viaje_pendiente_falla(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="PENDIENTE"))
    ok = viaje_repo.finalizar(vid, 5, 10)
    assert ok is False


def test_listar_finalizados_por_conductor(mongo_clean):
    from src.repositories import viaje_repo
    vid1 = viaje_repo.crear(_viaje_template(conductor_id="CON-X", estado="EN_CURSO"))
    viaje_repo.finalizar(vid1, 5, 10)
    vid2 = viaje_repo.crear(_viaje_template(conductor_id="CON-X", estado="EN_CURSO"))
    viaje_repo.finalizar(vid2, 5, 10)
    viaje_repo.crear(_viaje_template(conductor_id="CON-Y", estado="EN_CURSO"))
    viajes_x = viaje_repo.listar_finalizados_por_conductor("CON-X")
    assert len(viajes_x) == 2


def test_contar_por_pareja(mongo_clean):
    from src.repositories import viaje_repo
    for _ in range(3):
        vid = viaje_repo.crear(_viaje_template(usuario_id="U", conductor_id="C", estado="EN_CURSO"))
        viaje_repo.finalizar(vid, 5, 10)
    viaje_repo.crear(_viaje_template(usuario_id="U", conductor_id="OTRO", estado="PENDIENTE"))
    assert viaje_repo.contar_por_pareja("U", "C") == 3
    assert viaje_repo.contar_por_pareja("U", "OTRO") == 0  # no finalizados
