"""Tests del auth_service (Postgres + Mongo + Redis + Neo4j)."""
import pytest


# ---- register_usuario ----

def test_register_usuario_persiste_en_postgres(postgres_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo

    uid = auth_service.register_usuario("juan@m.com", "pass1234", "Juan")
    user = usuario_repo.get_by_id(uid)
    assert user is not None
    assert user["email"] == "juan@m.com"
    assert user["nombre"] == "Juan"
    assert user["password_hash"] != "pass1234"  # debe estar hasheado


def test_register_usuario_crea_nodo_neo4j(postgres_clean, neo4j_clean):
    from src.services import auth_service
    from src.db.neo4j_db import get_driver

    uid = auth_service.register_usuario("ana@m.com", "p", "Ana")
    with get_driver().session() as s:
        n = s.run("MATCH (u:Usuario {id:$id}) RETURN u", id=uid).single()
        assert n is not None


def test_register_usuario_email_duplicado_lanza_error(postgres_clean, neo4j_clean):
    from src.services import auth_service
    import psycopg
    auth_service.register_usuario("dup@m.com", "p", "Juan")
    with pytest.raises(psycopg.errors.UniqueViolation):
        auth_service.register_usuario("dup@m.com", "p", "Otro Juan")


# ---- register_conductor ----

def test_register_conductor_persiste_en_postgres_y_neo4j(postgres_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import conductor_repo
    from src.db.neo4j_db import get_driver

    cid = auth_service.register_conductor("ana@m.com", "pass", "Ana", "LIC-001")
    assert conductor_repo.get_by_id(cid) is not None
    with get_driver().session() as s:
        n = s.run("MATCH (c:Conductor {id:$id}) RETURN c", id=cid).single()
        assert n is not None


# ---- login ----

def test_login_usuario_devuelve_token(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service

    auth_service.register_usuario("user@m.com", "secret123", "User")
    token = auth_service.login("user@m.com", "secret123", "USUARIO")
    assert token is not None and len(token) >= 16


def test_login_crea_sesion_en_redis(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import cache_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    sesion = cache_repo.get_session(token)
    assert sesion is not None
    assert sesion["tipo"] == "USUARIO"


def test_login_registra_evento_en_mongo(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo, login_history_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    auth_service.login("u@m.com", "p", "USUARIO")
    uid = usuario_repo.get_by_email("u@m.com")["id"]
    eventos = login_history_repo.listar_por_usuario(uid)
    assert any(e["evento"] == "LOGIN_OK" for e in eventos)


def test_login_password_incorrecto_lanza_credenciales_invalidas(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.utils.errors import CredencialesInvalidas

    auth_service.register_usuario("u@m.com", "secret", "U")
    with pytest.raises(CredencialesInvalidas):
        auth_service.login("u@m.com", "incorrecto", "USUARIO")


def test_login_password_incorrecto_registra_evento_fail(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo, login_history_repo
    from src.utils.errors import CredencialesInvalidas

    auth_service.register_usuario("u@m.com", "secret", "U")
    with pytest.raises(CredencialesInvalidas):
        auth_service.login("u@m.com", "wrong", "USUARIO")
    uid = usuario_repo.get_by_email("u@m.com")["id"]
    eventos = login_history_repo.listar_por_usuario(uid)
    assert any(e["evento"] == "LOGIN_FAIL" for e in eventos)


def test_login_email_inexistente_lanza_error(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.utils.errors import CredencialesInvalidas

    with pytest.raises(CredencialesInvalidas):
        auth_service.login("no@m.com", "p", "USUARIO")


# ---- validate_session ----

def test_validate_session_existente(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    sesion = auth_service.validate_session(token)
    assert sesion is not None
    assert sesion["tipo"] == "USUARIO"


def test_validate_session_inexistente(redis_clean):
    from src.services import auth_service
    assert auth_service.validate_session("token-falso") is None


# ---- logout ----

def test_logout_borra_sesion_en_redis(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import cache_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    assert cache_repo.get_session(token) is not None
    auth_service.logout(token)
    assert cache_repo.get_session(token) is None


def test_logout_registra_evento_en_mongo(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo, login_history_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    auth_service.logout(token)
    uid = usuario_repo.get_by_email("u@m.com")["id"]
    eventos = login_history_repo.listar_por_usuario(uid)
    assert any(e["evento"] == "LOGOUT" for e in eventos)
