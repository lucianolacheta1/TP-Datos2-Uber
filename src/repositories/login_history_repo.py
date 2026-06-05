"""Repository de Login History (Mongo). Auditoría de logins/logouts."""
from datetime import datetime, UTC
from src.db.mongo import get_db


def _coll():
    return get_db().login_history


def crear(usuario_id: str, tipo_cuenta: str, evento: str,
          ip: str | None = None) -> str:
    """Registra un evento de login/logout/fail."""
    doc = {
        "usuario_id": usuario_id,
        "tipo_cuenta": tipo_cuenta,
        "evento": evento,
        "ip": ip,
        "timestamp": datetime.now(UTC),
    }
    return str(_coll().insert_one(doc).inserted_id)


def listar_por_usuario(usuario_id: str, limit: int = 10) -> list[dict]:
    """Devuelve los últimos N eventos de un usuario, más reciente primero."""
    docs = _coll().find({"usuario_id": usuario_id}).sort("timestamp", -1).limit(limit)
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result
