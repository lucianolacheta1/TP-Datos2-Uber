"""Tests del usuario_repo (Postgres)."""
import pytest


# ---- crear ----

def test_crear_devuelve_id(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("juan@mail.com", "hash123", "Juan Pérez")
    assert id is not None
    assert len(id) == 36  # UUID


def test_crear_persiste_los_datos(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("ana@mail.com", "hash456", "Ana Gómez", "+541112345678")
    user = usuario_repo.get_by_id(id)
    assert user["email"] == "ana@mail.com"
    assert user["nombre"] == "Ana Gómez"
    assert user["telefono"] == "+541112345678"


def test_crear_email_duplicado_lanza_error(postgres_clean):
    from src.repositories import usuario_repo
    import psycopg
    usuario_repo.crear("dup@mail.com", "hash", "Primer Juan")
    with pytest.raises(psycopg.errors.UniqueViolation):
        usuario_repo.crear("dup@mail.com", "hash2", "Segundo Juan")


# ---- get_by_id ----

def test_get_by_id_no_existente_devuelve_none(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.get_by_id("00000000-0000-0000-0000-000000000000") is None


def test_get_by_id_existente_devuelve_dict(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("test@mail.com", "h", "Test")
    user = usuario_repo.get_by_id(id)
    assert user is not None
    assert user["id"] == id
    assert user["email"] == "test@mail.com"


# ---- get_by_email ----

def test_get_by_email_existente(postgres_clean):
    from src.repositories import usuario_repo
    usuario_repo.crear("mail@mail.com", "h", "Mail")
    user = usuario_repo.get_by_email("mail@mail.com")
    assert user["nombre"] == "Mail"


def test_get_by_email_no_existente(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.get_by_email("inexistente@mail.com") is None


# ---- actualizar_rating ----

def test_actualizar_rating_existente(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("rate@mail.com", "h", "Rate")
    ok = usuario_repo.actualizar_rating(id, 4.5)
    assert ok is True
    assert usuario_repo.get_by_id(id)["rating_promedio"] == pytest.approx(4.5)


def test_actualizar_rating_no_existente(postgres_clean):
    from src.repositories import usuario_repo
    ok = usuario_repo.actualizar_rating("00000000-0000-0000-0000-000000000000", 5)
    assert ok is False


# ---- listar_todos ----

def test_listar_todos_vacio(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.listar_todos() == []


def test_listar_todos_con_varios(postgres_clean):
    from src.repositories import usuario_repo
    usuario_repo.crear("a@mail.com", "h", "A")
    usuario_repo.crear("b@mail.com", "h", "B")
    usuario_repo.crear("c@mail.com", "h", "C")
    todos = usuario_repo.listar_todos()
    assert len(todos) == 3
    emails = sorted(u["email"] for u in todos)
    assert emails == ["a@mail.com", "b@mail.com", "c@mail.com"]


# ---- existe ----

def test_existe_true(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("e@mail.com", "h", "E")
    assert usuario_repo.existe(id) is True


def test_existe_false(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.existe("00000000-0000-0000-0000-000000000000") is False
