"""Limpia (vacía) las 5 bases de datos del proyecto. SOLO PARA DESARROLLO.

Uso:
    python -m scripts.reset_all_dbs

Pide confirmación interactiva antes de borrar.
"""
import sys
from src.config import settings, validate
from src.db import postgres, mongo, cassandra, neo4j_db, redis_db
from src.utils.logger import logger


def reset_postgres():
    with postgres.get_conn().cursor() as cur:
        cur.execute("TRUNCATE vehiculo, conductor, usuario CASCADE;")
    logger.info("Postgres: tablas truncadas")


def reset_mongo():
    db = mongo.get_db()
    for coll in ["viajes", "pagos", "resenas", "login_history"]:
        db[coll].drop()
    logger.info("Mongo: colecciones dropeadas")


def reset_cassandra():
    session = cassandra.get_session()
    for table in ["ubicaciones_por_vehiculo", "ultima_actividad_conductor", "viajes_finalizados_por_dia"]:
        session.execute(f"TRUNCATE {table}")
    logger.info("Cassandra: tablas truncadas")


def reset_neo4j():
    with neo4j_db.get_driver().session() as s:
        s.run("MATCH (n) DETACH DELETE n")
    logger.info("Neo4j: nodos y aristas borrados")


def reset_redis():
    redis_db.get_client().flushdb()
    logger.info("Redis: FLUSHDB ejecutado")


def main() -> int:
    validate()

    print("ATENCION: este script va a borrar TODOS los datos de las 5 bases:")
    print(f"   Postgres ({settings.POSTGRES_URL[:40]}...)")
    print(f"   Mongo    ({settings.MONGO_URL[:40]}...)")
    print(f"   Cassandra keyspace: {settings.ASTRA_KEYSPACE}")
    print(f"   Neo4j    ({settings.NEO4J_URI})")
    print(f"   Redis    ({settings.REDIS_HOST})")
    print()
    confirm = input('Escribí exactamente "BORRAR" para confirmar: ')
    if confirm != "BORRAR":
        print("Cancelado.")
        return 1

    reset_postgres()
    reset_mongo()
    reset_cassandra()
    reset_neo4j()
    reset_redis()

    print("\nLimpieza completa.")
    print("Recordá correr `python -m scripts.init_mongo` para recrear los índices de Mongo (los demás esquemas se preservan).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
