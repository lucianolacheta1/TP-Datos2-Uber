"""Reconciliation service: rebuild de proyecciones desde el SOT.

Garantiza eventual consistency entre Mongo (SOT de viajes) y las bases
derivadas (Neo4j para el caso 5, principalmente).

Modos de uso:
- Manual desde el menú admin del Plan 04.
- Periódico (no implementado en el TP — el menú alcanza).
"""
from src.db.mongo import get_db
from src.db.neo4j_db import get_driver
from src.utils import outbox
from src.utils.logger import logger


def sync_neo4j_desde_mongo() -> dict:
    """Reconstruye las aristas VIAJO_CON en Neo4j desde Mongo.

    Devuelve {'pares_reconstruidos': N, 'viajes_procesados': M}.
    """
    # 1. Agregar viajes finalizados por pareja en Mongo
    pipeline = [
        {"$match": {"estado": "FINALIZADO"}},
        {"$group": {
            "_id": {"u": "$usuario_id", "c": "$conductor_id"},
            "n":   {"$sum": 1},
        }},
    ]
    pares = list(get_db().viajes.aggregate(pipeline))
    total_viajes = sum(p["n"] for p in pares)

    # 2. Aplicar a Neo4j (borra + recrea aristas)
    with get_driver().session() as s:
        # Borrar todas las aristas VIAJO_CON (deja los nodos)
        s.run("MATCH ()-[r:VIAJO_CON]->() DELETE r")
        # Recrear con los conteos correctos
        for par in pares:
            s.run(
                """
                MERGE (u:Usuario   {id: $uid})
                MERGE (c:Conductor {id: $cid})
                MERGE (u)-[r:VIAJO_CON]->(c)
                SET r.cantidad_viajes = $n
                """,
                uid=par["_id"]["u"],
                cid=par["_id"]["c"],
                n=par["n"],
            )

    logger.info(f"Reconciliación: {len(pares)} pares, {total_viajes} viajes")
    return {"pares_reconstruidos": len(pares), "viajes_procesados": total_viajes}


def procesar_outbox() -> dict:
    """Reporta cuántas entradas hay pendientes en el outbox.

    Para el TP no implementamos retries automáticos — el flujo es:
    ver pendientes → correr sync_neo4j_desde_mongo() → outbox.clear().
    """
    pendientes = outbox.pending()
    return {"pendientes": len(pendientes), "entradas": pendientes}
