"""Repository de Usuario (Postgres).

Solo CRUD y queries. Sin lógica de negocio.
"""
from src.db.postgres import get_conn


def crear(email: str, password_hash: str, nombre: str,
          telefono: str | None = None, foto_url: str | None = None) -> str:
    """Inserta un nuevo usuario y devuelve su id (UUID como str)."""
    sql = """
        INSERT INTO usuario (email, password_hash, nombre, telefono, foto_url)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id::text
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (email, password_hash, nombre, telefono, foto_url))
        return cur.fetchone()[0]


def get_by_id(id: str) -> dict | None:
    """Devuelve el usuario o None."""
    sql = """
        SELECT id::text, email, password_hash, nombre, telefono, foto_url,
               rating_promedio, fecha_registro, estado
        FROM usuario WHERE id = %s
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def get_by_email(email: str) -> dict | None:
    """Devuelve el usuario por email o None."""
    sql = """
        SELECT id::text, email, password_hash, nombre, telefono, foto_url,
               rating_promedio, fecha_registro, estado
        FROM usuario WHERE email = %s
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (email,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def actualizar_rating(id: str, nuevo_rating: float) -> bool:
    """Actualiza rating_promedio. Devuelve True si modificó una fila."""
    sql = "UPDATE usuario SET rating_promedio = %s WHERE id = %s"
    with get_conn().cursor() as cur:
        cur.execute(sql, (nuevo_rating, id))
        return cur.rowcount == 1


def listar_todos() -> list[dict]:
    """Devuelve todos los usuarios (lista vacía si no hay)."""
    sql = """
        SELECT id::text, email, nombre, telefono, rating_promedio, estado
        FROM usuario ORDER BY fecha_registro
    """
    with get_conn().cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def existe(id: str) -> bool:
    """Devuelve True si existe un usuario con ese id."""
    sql = "SELECT 1 FROM usuario WHERE id = %s"
    with get_conn().cursor() as cur:
        cur.execute(sql, (id,))
        return cur.fetchone() is not None
