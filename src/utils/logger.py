"""Logger configurado del proyecto."""
import logging
from src.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Silenciar el ruido de los drivers de terceros: emiten muchos INFO/WARNING
# esperados (downgrade de protocolo de Cassandra, "USE keyspace", notificaciones
# de producto cartesiano de Neo4j, heartbeats de pools, etc.). Dejamos solo
# nuestros logs (tp_uber) y los errores reales de cada driver.
for _ruidoso in ("cassandra", "neo4j", "neo4j.notifications", "neo4j.pool",
                 "neo4j.io", "pymongo", "pymongo.topology", "urllib3"):
    logging.getLogger(_ruidoso).setLevel(logging.ERROR)

logger = logging.getLogger("tp_uber")
