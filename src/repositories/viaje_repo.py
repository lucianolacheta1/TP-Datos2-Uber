"""Repository de Viaje (Mongo)."""
from datetime import datetime, UTC
from bson import ObjectId
from src.db.mongo import get_db


def _coll():
    return get_db().viajes


def crear(viaje_doc: dict) -> str:
    """Inserta el documento y devuelve el _id como str."""
    return str(_coll().insert_one(viaje_doc).inserted_id)


def get_by_id(id: str) -> dict | None:
    """Devuelve el viaje por id (ObjectId str) o None."""
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    doc = _coll().find_one({"_id": oid})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def iniciar(id: str) -> bool:
    """Transición PENDIENTE → EN_CURSO. True si modificó."""
    res = _coll().update_one(
        {"_id": ObjectId(id), "estado": "PENDIENTE"},
        {"$set": {"estado": "EN_CURSO", "ts_inicio": datetime.now(UTC)}}
    )
    return res.modified_count == 1


def finalizar(id: str, distancia_km: float, duracion_min: int) -> bool:
    """Transición EN_CURSO → FINALIZADO. True si modificó."""
    res = _coll().update_one(
        {"_id": ObjectId(id), "estado": "EN_CURSO"},
        {"$set": {
            "estado": "FINALIZADO",
            "distancia_km": distancia_km,
            "duracion_min": duracion_min,
            "ts_fin": datetime.now(UTC),
        }}
    )
    return res.modified_count == 1


def listar_finalizados_por_conductor(conductor_id: str) -> list[dict]:
    docs = _coll().find({"conductor_id": conductor_id, "estado": "FINALIZADO"})
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result


def contar_por_pareja(usuario_id: str, conductor_id: str) -> int:
    return _coll().count_documents({
        "usuario_id": usuario_id,
        "conductor_id": conductor_id,
        "estado": "FINALIZADO",
    })


def listar_finalizados() -> list[dict]:
    docs = _coll().find({"estado": "FINALIZADO"})
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result
