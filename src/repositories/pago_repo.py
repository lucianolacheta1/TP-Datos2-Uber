"""Repository de Pago (Mongo)."""
from bson import ObjectId
from src.db.mongo import get_db


def _coll():
    return get_db().pagos


def crear(pago_doc: dict) -> str:
    return str(_coll().insert_one(pago_doc).inserted_id)


def get_by_id(id: str) -> dict | None:
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    doc = _coll().find_one({"_id": oid})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def get_by_viaje_id(viaje_id: str) -> dict | None:
    doc = _coll().find_one({"viaje_id": viaje_id})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def contar_por_metodo() -> dict:
    """Devuelve {metodo_pago: cantidad}."""
    pipeline = [
        {"$group": {"_id": "$metodo_pago", "c": {"$sum": 1}}},
    ]
    return {doc["_id"]: doc["c"] for doc in _coll().aggregate(pipeline)}


def metodo_menos_usado() -> str | None:
    """Caso de uso 2: método con menos pagos."""
    pipeline = [
        {"$group": {"_id": "$metodo_pago", "c": {"$sum": 1}}},
        {"$sort": {"c": 1}},
        {"$limit": 1},
    ]
    result = list(_coll().aggregate(pipeline))
    return result[0]["_id"] if result else None
