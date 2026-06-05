"""Tests del cache_repo (Redis)."""
import time


def test_set_y_get_session(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_session("token-abc", {"user_id": "U1", "tipo": "USUARIO"})
    data = cache_repo.get_session("token-abc")
    assert data == {"user_id": "U1", "tipo": "USUARIO"}


def test_get_session_no_existente(redis_clean):
    from src.repositories import cache_repo
    assert cache_repo.get_session("no-existe") is None


def test_session_expira_con_ttl(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_session("token", {"u": "x"}, ttl_seconds=1)
    assert cache_repo.get_session("token") is not None
    time.sleep(1.2)
    assert cache_repo.get_session("token") is None


def test_delete_session(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_session("t", {"u": "x"})
    cache_repo.delete_session("t")
    assert cache_repo.get_session("t") is None


def test_set_y_get_ultima_pos(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_ultima_pos("V1", -34.6, -58.4)
    pos = cache_repo.get_ultima_pos("V1")
    assert pos == (-34.6, -58.4)


def test_get_ultima_pos_no_existente(redis_clean):
    from src.repositories import cache_repo
    assert cache_repo.get_ultima_pos("V-no") is None


def test_set_y_get_cache(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_cache("top3", [{"autor": "A"}, {"autor": "B"}])
    assert cache_repo.get_cache("top3") == [{"autor": "A"}, {"autor": "B"}]


def test_invalidar_cache(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_cache("k", "v")
    cache_repo.invalidar("k")
    assert cache_repo.get_cache("k") is None
