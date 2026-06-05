"""Repository de Resena (Mongo)."""
from bson import ObjectId
from src.db.mongo import get_db


def _coll():
    return get_db().resenas


def crear(resena_doc: dict) -> str:
    return str(_coll().insert_one(resena_doc).inserted_id)


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


def top_autores(n: int = 3, tipo: str = "U_A_C") -> list[dict]:
    """Caso de uso 1: top N autores con más reseñas del tipo dado."""
    pipeline = [
        {"$match": {"tipo": tipo}},
        {"$group": {"_id": "$autor.id", "cantidad": {"$sum": 1}}},
        {"$sort": {"cantidad": -1}},
        {"$limit": n},
    ]
    return [
        {"autor_id": doc["_id"], "cantidad": doc["cantidad"]}
        for doc in _coll().aggregate(pipeline)
    ]


def buscar_por_rating_extremo() -> list[dict]:
    """Caso de uso 7: reseñas con rating = 5 o rating < 2."""
    docs = _coll().find({"$or": [{"rating": 5}, {"rating": {"$lt": 2}}]})
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result


def ratings_de_destinatario(destinatario_id: str) -> list[int]:
    """Devuelve la lista de ratings de un destinatario (para recalcular promedio)."""
    cursor = _coll().find(
        {"destinatario.id": destinatario_id},
        projection={"_id": 0, "rating": 1}
    )
    return [d["rating"] for d in cursor]
