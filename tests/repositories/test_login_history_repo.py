"""Tests del login_history_repo (Mongo)."""


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import login_history_repo
    rid = login_history_repo.crear("U1", "USUARIO", "LOGIN_OK", "190.x.x.x")
    assert rid is not None and len(rid) == 24


def test_listar_por_usuario(mongo_clean):
    from src.repositories import login_history_repo
    login_history_repo.crear("U1", "USUARIO", "LOGIN_OK")
    login_history_repo.crear("U1", "USUARIO", "LOGOUT")
    login_history_repo.crear("U2", "USUARIO", "LOGIN_OK")
    eventos = login_history_repo.listar_por_usuario("U1")
    assert len(eventos) == 2


def test_listar_por_usuario_orden_desc(mongo_clean):
    from src.repositories import login_history_repo
    import time
    login_history_repo.crear("U", "USUARIO", "LOGIN_OK")
    time.sleep(0.01)
    login_history_repo.crear("U", "USUARIO", "LOGOUT")
    eventos = login_history_repo.listar_por_usuario("U")
    # El más reciente primero
    assert eventos[0]["evento"] == "LOGOUT"


def test_listar_respeta_limit(mongo_clean):
    from src.repositories import login_history_repo
    for i in range(15):
        login_history_repo.crear("U", "USUARIO", "LOGIN_OK")
    eventos = login_history_repo.listar_por_usuario("U", limit=5)
    assert len(eventos) == 5
