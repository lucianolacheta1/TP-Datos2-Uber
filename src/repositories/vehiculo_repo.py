"""Repository de Vehiculo (Postgres)."""
from src.db.postgres import get_conn

_COLS = """
    id::text, conductor_id::text, placa, marca, modelo,
    anio, color, tipo
"""


def crear(conductor_id: str, placa: str, marca: str, modelo: str,
          anio: int | None = None, color: str | None = None,
          tipo: str | None = None) -> str:
    sql = """
        INSERT INTO vehiculo (conductor_id, placa, marca, modelo, anio, color, tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id::text
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (conductor_id, placa, marca, modelo, anio, color, tipo))
        return cur.fetchone()[0]


def get_by_id(id: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo WHERE id = %s", (id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def get_by_placa(placa: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo WHERE placa = %s", (placa,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def listar_por_conductor(conductor_id: str) -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo WHERE conductor_id = %s", (conductor_id,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def listar_todos() -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def existe(id: str) -> bool:
    with get_conn().cursor() as cur:
        cur.execute("SELECT 1 FROM vehiculo WHERE id = %s", (id,))
        return cur.fetchone() is not None
