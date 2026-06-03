"""Tests del conductor_repo (Postgres)."""
import pytest


def test_crear_devuelve_id(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("ana@mail.com", "h", "Ana", "LIC-001")
    assert id is not None and len(id) == 36


def test_crear_persiste_los_datos(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("p@mail.com", "h", "Pedro", "LIC-002", "+54999")
    c = conductor_repo.get_by_id(id)
    assert c["email"] == "p@mail.com"
    assert c["nro_licencia"] == "LIC-002"
    assert c["telefono"] == "+54999"


def test_crear_licencia_duplicada_lanza_error(postgres_clean):
    from src.repositories import conductor_repo
    import psycopg
    conductor_repo.crear("c1@mail.com", "h", "C1", "LIC-DUP")
    with pytest.raises(psycopg.errors.UniqueViolation):
        conductor_repo.crear("c2@mail.com", "h", "C2", "LIC-DUP")


def test_get_by_id_no_existente(postgres_clean):
    from src.repositories import conductor_repo
    assert conductor_repo.get_by_id("00000000-0000-0000-0000-000000000000") is None


def test_get_by_email_existente(postgres_clean):
    from src.repositories import conductor_repo
    conductor_repo.crear("e@mail.com", "h", "E", "LIC-E")
    c = conductor_repo.get_by_email("e@mail.com")
    assert c["nro_licencia"] == "LIC-E"


def test_actualizar_rating_existente(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("r@mail.com", "h", "R", "LIC-R")
    ok = conductor_repo.actualizar_rating(id, 4.8)
    assert ok is True
    assert conductor_repo.get_by_id(id)["rating_promedio"] == pytest.approx(4.8)


def test_listar_todos_vacio(postgres_clean):
    from src.repositories import conductor_repo
    assert conductor_repo.listar_todos() == []


def test_listar_todos_con_varios(postgres_clean):
    from src.repositories import conductor_repo
    conductor_repo.crear("a@m.com", "h", "A", "L1")
    conductor_repo.crear("b@m.com", "h", "B", "L2")
    assert len(conductor_repo.listar_todos()) == 2


def test_listar_activos_excluye_baja(postgres_clean):
    from src.repositories import conductor_repo
    from src.db.postgres import get_conn
    id1 = conductor_repo.crear("act@m.com", "h", "Act", "L-ACT")
    id2 = conductor_repo.crear("baj@m.com", "h", "Baj", "L-BAJ")
    with get_conn().cursor() as cur:
        cur.execute("UPDATE conductor SET estado = 'BAJA' WHERE id = %s", (id2,))
    activos = conductor_repo.listar_activos()
    ids = [c["id"] for c in activos]
    assert id1 in ids
    assert id2 not in ids


def test_existe_true_y_false(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("e@m.com", "h", "E", "L-E")
    assert conductor_repo.existe(id) is True
    assert conductor_repo.existe("00000000-0000-0000-0000-000000000000") is False
