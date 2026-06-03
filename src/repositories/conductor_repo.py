"""Repository de Conductor (Postgres)."""
from src.db.postgres import get_conn

_COLS_FULL = """
    id::text, email, password_hash, nombre, telefono, nro_licencia,
    rating_promedio, estado, fecha_registro
"""


def crear(email: str, password_hash: str, nombre: str, nro_licencia: str,
          telefono: str | None = None) -> str:
    sql = """
        INSERT INTO conductor (email, password_hash, nombre, nro_licencia, telefono)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id::text
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (email, password_hash, nombre, nro_licencia, telefono))
        return cur.fetchone()[0]


def get_by_id(id: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor WHERE id = %s", (id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def get_by_email(email: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor WHERE email = %s", (email,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def actualizar_rating(id: str, nuevo_rating: float) -> bool:
    sql = "UPDATE conductor SET rating_promedio = %s WHERE id = %s"
    with get_conn().cursor() as cur:
        cur.execute(sql, (nuevo_rating, id))
        return cur.rowcount == 1


def listar_todos() -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor ORDER BY fecha_registro")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def listar_activos() -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor WHERE estado = 'ACTIVO' ORDER BY fecha_registro")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def existe(id: str) -> bool:
    with get_conn().cursor() as cur:
        cur.execute("SELECT 1 FROM conductor WHERE id = %s", (id,))
        return cur.fetchone() is not None
