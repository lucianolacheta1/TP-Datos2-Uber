"""Verifica que las 5 conexiones a las bases de datos funcionan.

Uso:
    python -m scripts.check_connections

Exit code 0 si todas OK, 1 si alguna falla.
"""
import sys
from src.config import validate
from src.db import postgres, mongo, cassandra, neo4j_db, redis_db


def main() -> int:
    print("Validando .env...")
    try:
        validate()
        print("OK\n")
    except RuntimeError as e:
        print(f"FAIL: {e}")
        return 1

    bases = [
        ("Postgres   (Neon)",   postgres.check),
        ("MongoDB    (Atlas)",  mongo.check),
        ("Cassandra  (Astra)",  cassandra.check),
        ("Neo4j      (Aura)",   neo4j_db.check),
        ("Redis      (Cloud)",  redis_db.check),
    ]

    print("Verificando conexiones a las bases:")
    todos_ok = True
    for nombre, check_fn in bases:
        ok = check_fn()
        estado = "OK  " if ok else "FAIL"
        print(f"  [{estado}] {nombre}")
        if not ok:
            todos_ok = False

    print()
    if todos_ok:
        print("Todas las bases respondieron correctamente.")
        return 0
    else:
        print("Hay bases con problemas. Revisar logs y credenciales.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
