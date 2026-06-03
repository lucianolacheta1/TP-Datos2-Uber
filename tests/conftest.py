"""Fixtures globales para todos los tests del proyecto.

Cada fixture limpia su base de datos antes del test. Esto garantiza
aislamiento entre tests aún cuando ejecutan contra DBs reales en cloud.

Uso en un test:

    def test_algo(postgres_clean):
        # Postgres está vacía acá
        ...
"""
import pytest


@pytest.fixture
def postgres_clean():
    """Trunca todas las tablas de Postgres antes del test."""
    from src.db.postgres import get_conn
    with get_conn().cursor() as cur:
        cur.execute("TRUNCATE vehiculo, conductor, usuario CASCADE;")
    yield


@pytest.fixture
def mongo_clean():
    """Borra todas las colecciones de Mongo antes del test."""
    from src.db.mongo import get_db
    db = get_db()
    for coll in ["viajes", "pagos", "resenas", "login_history"]:
        db[coll].drop()
    # Recrear índices después de drop (los pierde con drop_collection)
    db.viajes.create_index([("usuario_id", 1)])
    db.viajes.create_index([("conductor_id", 1)])
    db.viajes.create_index([("estado", 1), ("ts_inicio", -1)])
    db.pagos.create_index([("viaje_id", 1)])
    db.pagos.create_index([("metodo_pago", 1)])
    db.resenas.create_index([("autor.id", 1)])
    db.resenas.create_index([("destinatario.id", 1)])
    db.resenas.create_index([("tipo", 1), ("rating", 1)])
    yield


@pytest.fixture
def cassandra_clean():
    """Trunca todas las tablas de Cassandra antes del test."""
    from src.db.cassandra import get_session
    session = get_session()
    for table in ["ubicaciones_por_vehiculo", "ultima_actividad_conductor",
                  "viajes_finalizados_por_dia"]:
        session.execute(f"TRUNCATE {table}")
    yield


@pytest.fixture
def neo4j_clean():
    """Borra todos los nodos y aristas de Neo4j antes del test."""
    from src.db.neo4j_db import get_driver
    with get_driver().session() as s:
        s.run("MATCH (n) DETACH DELETE n")
    yield


@pytest.fixture
def redis_clean():
    """FLUSHDB en Redis antes del test."""
    from src.db.redis_db import get_client
    get_client().flushdb()
    yield
