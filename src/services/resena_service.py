"""Resena service: crear reseñas con propagación a Postgres/Neo4j/Redis.

Toca:
- Mongo    → viajes (lectura), resenas (SOT).
- Postgres → update rating_promedio del destinatario.
- Neo4j    → update rating en nodo Conductor (si aplica).
- Redis    → invalida cache:top3_resenadores.
"""
from datetime import datetime, UTC

from src.repositories import (
    viaje_repo, resena_repo,
    usuario_repo, conductor_repo, grafo_repo, cache_repo,
)
from src.utils import outbox
from src.utils.errors import ViajeNoEncontrado, EstadoInvalido
from src.utils.logger import logger
from src.db.neo4j_db import get_driver


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


def crear(viaje_id: str, tipo: str,
          autor_id: str, autor_nombre: str,
          destinatario_id: str, destinatario_nombre: str,
          rating: int, comentario: str) -> str:
    """Crea una reseña y propaga el nuevo rating al destinatario.

    tipo: 'U_A_C' (Usuario a Conductor) o 'C_A_U' (Conductor a Usuario).
    rating: 1 a 5.
    """
    viaje = viaje_repo.get_by_id(viaje_id)
    if viaje is None:
        raise ViajeNoEncontrado(viaje_id)
    if viaje["estado"] != "FINALIZADO":
        raise EstadoInvalido(f"Solo se puede reseñar viajes FINALIZADOS (actual: {viaje['estado']})")

    # 1. SOT: insertar reseña en Mongo
    doc = {
        "viaje_id": viaje_id,
        "tipo": tipo,
        "autor":        {"id": autor_id,        "nombre": autor_nombre},
        "destinatario": {"id": destinatario_id, "nombre": destinatario_nombre},
        "rating": rating,
        "comentario": comentario,
        "timestamp": datetime.now(UTC),
        "contexto_viaje": {
            "origen": viaje["origen"].get("direccion", ""),
            "destino": viaje["destino"].get("direccion", ""),
            "duracion_min": viaje.get("duracion_min"),
        },
    }
    rid = resena_repo.crear(doc)

    # 2. Recalcular promedio del destinatario
    ratings = resena_repo.ratings_de_destinatario(destinatario_id)
    nuevo_promedio = sum(ratings) / len(ratings) if ratings else 0

    # 3. Actualizar Postgres (rating_promedio)
    if tipo == "U_A_C":
        # destinatario es conductor
        _intentar("postgres_update_rating_conductor",
                  lambda: conductor_repo.actualizar_rating(destinatario_id, nuevo_promedio))
        # 4. Actualizar Neo4j (rating en nodo Conductor)
        _intentar("neo4j_update_rating_conductor",
                  lambda: _actualizar_rating_neo4j_conductor(destinatario_id, nuevo_promedio))
    else:
        # destinatario es usuario
        _intentar("postgres_update_rating_usuario",
                  lambda: usuario_repo.actualizar_rating(destinatario_id, nuevo_promedio))

    # 5. Invalidar cache top3
    _intentar("redis_invalidar_top3_resenadores",
              lambda: cache_repo.invalidar("top3_resenadores"))

    return rid


def _actualizar_rating_neo4j_conductor(conductor_id: str, rating: float) -> None:
    """Helper interno: SET rating en el nodo (:Conductor) de Neo4j."""
    cypher = "MATCH (c:Conductor {id: $id}) SET c.rating = $rating"
    with get_driver().session() as s:
        s.run(cypher, id=conductor_id, rating=rating)
