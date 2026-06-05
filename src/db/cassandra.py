"""Cassandra (DataStax Astra) connection — singleton."""
from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from src.config import settings
from src.utils.logger import logger

_session: Session | None = None

def get_session() -> Session:
    """Devuelve la sesion Cassandra (la crea la primera vez)."""
    global _session
    if _session is None:
        cloud_config = {"secure_connect_bundle": settings.ASTRA_BUNDLE_PATH}
        auth = PlainTextAuthProvider("token", settings.ASTRA_TOKEN)
        cluster = Cluster(cloud=cloud_config, auth_provider=auth)
        _session = cluster.connect(settings.ASTRA_KEYSPACE)
        logger.info("Conexion a Cassandra (Astra) establecida")
    return _session

def check() -> bool:
    """Devuelve True si la sesion y la query basica funcionan."""
    try:
        result = get_session().execute("SELECT release_version FROM system.local")
        return result.one() is not None
    except Exception as e:
        logger.error(f"Cassandra check failed: {e}")
        return False