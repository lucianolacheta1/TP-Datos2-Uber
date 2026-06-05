"""Tests del resena_repo (Mongo)."""
from datetime import datetime, UTC


def _resena_template(autor_id="A1", destinatario_id="D1", rating=5,
                     tipo="U_A_C", viaje_id="V1"):
    return {
        "viaje_id": viaje_id,
        "tipo": tipo,
        "autor": {"id": autor_id, "nombre": f"Autor {autor_id}"},
        "destinatario": {"id": destinatario_id, "nombre": f"Dest {destinatario_id}"},
        "rating": rating,
        "comentario": "Comentario de prueba",
        "timestamp": datetime.now(UTC),
        "contexto_viaje": {"origen": "A", "destino": "B", "duracion_min": 20},
    }


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import resena_repo
    rid = resena_repo.crear(_resena_template())
    assert rid is not None and len(rid) == 24


def test_get_by_id(mongo_clean):
    from src.repositories import resena_repo
    rid = resena_repo.crear(_resena_template(rating=4))
    r = resena_repo.get_by_id(rid)
    assert r["rating"] == 4


def test_top_autores_devuelve_top_3(mongo_clean):
    from src.repositories import resena_repo
    # Autor A: 5 reseñas; Autor B: 3; Autor C: 2; Autor D: 1
    for _ in range(5):
        resena_repo.crear(_resena_template(autor_id="A"))
    for _ in range(3):
        resena_repo.crear(_resena_template(autor_id="B"))
    for _ in range(2):
        resena_repo.crear(_resena_template(autor_id="C"))
    resena_repo.crear(_resena_template(autor_id="D"))
    top = resena_repo.top_autores(n=3, tipo="U_A_C")
    assert [t["autor_id"] for t in top] == ["A", "B", "C"]
    assert top[0]["cantidad"] == 5


def test_top_autores_filtra_por_tipo(mongo_clean):
    from src.repositories import resena_repo
    for _ in range(5):
        resena_repo.crear(_resena_template(autor_id="A", tipo="U_A_C"))
    for _ in range(10):
        resena_repo.crear(_resena_template(autor_id="X", tipo="C_A_U"))
    top = resena_repo.top_autores(n=3, tipo="U_A_C")
    assert top[0]["autor_id"] == "A"
    assert all(t["autor_id"] != "X" for t in top)


def test_buscar_por_rating_5_o_menor_2(mongo_clean):
    from src.repositories import resena_repo
    resena_repo.crear(_resena_template(rating=5))
    resena_repo.crear(_resena_template(rating=1))
    resena_repo.crear(_resena_template(rating=3))  # excluido
    resena_repo.crear(_resena_template(rating=4))  # excluido
    extremos = resena_repo.buscar_por_rating_extremo()
    assert len(extremos) == 2
    ratings = sorted(r["rating"] for r in extremos)
    assert ratings == [1, 5]


def test_ratings_de_destinatario(mongo_clean):
    from src.repositories import resena_repo
    resena_repo.crear(_resena_template(destinatario_id="DEST", rating=5))
    resena_repo.crear(_resena_template(destinatario_id="DEST", rating=4))
    resena_repo.crear(_resena_template(destinatario_id="DEST", rating=3))
    resena_repo.crear(_resena_template(destinatario_id="OTRO", rating=1))
    ratings = resena_repo.ratings_de_destinatario("DEST")
    assert sorted(ratings) == [3, 4, 5]
