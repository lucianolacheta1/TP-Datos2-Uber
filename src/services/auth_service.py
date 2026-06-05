"""Auth service: registro, login, logout, validación de sesión.

Toca:
- Postgres → cuentas (usuario, conductor) con password_hash bcrypt.
- Neo4j   → nodos (:Usuario), (:Conductor) (best-effort).
- Redis   → sesiones con TTL (10 min default).
- Mongo   → audit trail (login_history).
"""
import secrets
import bcrypt

from src.repositories import (
    usuario_repo, conductor_repo,
    grafo_repo, cache_repo, login_history_repo,
)
from src.utils import outbox
from src.utils.errors import CredencialesInvalidas
from src.utils.logger import logger


SESSION_TTL_SECONDS = 600  # 10 min


# ----------------- helpers -----------------

def _hash_password(password: str) -> str:
    """Hash bcrypt del password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _intentar(nombre: str, op) -> None:
    """Ejecuta una proyección best-effort, loguea y encola si falla."""
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


# ----------------- registro -----------------

def register_usuario(email: str, password: str, nombre: str,
                     telefono: str | None = None) -> str:
    """Crea un usuario en Postgres y proyecta a Neo4j."""
    pw_hash = _hash_password(password)
    user_id = usuario_repo.crear(email, pw_hash, nombre, telefono)
    _intentar("neo4j_crear_usuario",
              lambda: grafo_repo.crear_usuario(user_id, nombre, email))
    return user_id


def register_conductor(email: str, password: str, nombre: str,
                       nro_licencia: str, telefono: str | None = None) -> str:
    """Crea un conductor en Postgres y proyecta a Neo4j."""
    pw_hash = _hash_password(password)
    cond_id = conductor_repo.crear(email, pw_hash, nombre, nro_licencia, telefono)
    _intentar("neo4j_crear_conductor",
              lambda: grafo_repo.crear_conductor(cond_id, nombre, email, rating=0))
    return cond_id


# ----------------- login / logout -----------------

def login(email: str, password: str, tipo_cuenta: str) -> str:
    """Valida credenciales, genera token, abre sesión en Redis y audita en Mongo.

    tipo_cuenta: 'USUARIO' o 'CONDUCTOR'.
    Lanza CredencialesInvalidas si email/password no coinciden.
    """
    repo = usuario_repo if tipo_cuenta == "USUARIO" else conductor_repo
    cuenta = repo.get_by_email(email)

    if cuenta is None or not _verify_password(password, cuenta["password_hash"]):
        # Audit del fail (best-effort)
        if cuenta is not None:
            _intentar("mongo_login_fail",
                      lambda: login_history_repo.crear(
                          cuenta["id"], tipo_cuenta, "LOGIN_FAIL"))
        raise CredencialesInvalidas("Email o password incorrectos")

    # Token y sesión
    token = secrets.token_urlsafe(24)
    cache_repo.set_session(
        token,
        {"user_id": cuenta["id"], "tipo": tipo_cuenta, "nombre": cuenta["nombre"]},
        ttl_seconds=SESSION_TTL_SECONDS,
    )
    # Audit OK (best-effort)
    _intentar("mongo_login_ok",
              lambda: login_history_repo.crear(cuenta["id"], tipo_cuenta, "LOGIN_OK"))
    return token


def logout(token: str) -> None:
    """Borra la sesión en Redis y audita en Mongo."""
    sesion = cache_repo.get_session(token)
    cache_repo.delete_session(token)
    if sesion is not None:
        _intentar("mongo_logout",
                  lambda: login_history_repo.crear(
                      sesion["user_id"], sesion["tipo"], "LOGOUT"))


# ----------------- sesión -----------------

def validate_session(token: str) -> dict | None:
    """Devuelve los datos de sesión o None si expiró/no existe."""
    return cache_repo.get_session(token)
