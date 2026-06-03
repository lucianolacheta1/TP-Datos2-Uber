"""Repository de grafo (Neo4j). Nodos y relaciones de Usuario/Conductor/Vehiculo."""
from src.db.neo4j_db import get_driver


def crear_usuario(id: str, nombre: str, email: str) -> None:
    cypher = """
        MERGE (u:Usuario {id: $id})
        SET u.nombre = $nombre, u.email = $email
    """
    with get_driver().session() as s:
        s.run(cypher, id=id, nombre=nombre, email=email)


def crear_conductor(id: str, nombre: str, email: str, rating: float = 0) -> None:
    cypher = """
        MERGE (c:Conductor {id: $id})
        SET c.nombre = $nombre, c.email = $email, c.rating = $rating
    """
    with get_driver().session() as s:
        s.run(cypher, id=id, nombre=nombre, email=email, rating=rating)


def crear_vehiculo(id: str, placa: str, marca: str, modelo: str,
                   anio: int | None = None) -> None:
    cypher = """
        MERGE (v:Vehiculo {id: $id})
        SET v.placa = $placa, v.marca = $marca, v.modelo = $modelo, v.anio = $anio
    """
    with get_driver().session() as s:
        s.run(cypher, id=id, placa=placa, marca=marca, modelo=modelo, anio=anio)


def crear_relacion_maneja(conductor_id: str, vehiculo_id: str) -> None:
    cypher = """
        MATCH (c:Conductor {id: $cid}), (v:Vehiculo {id: $vid})
        MERGE (c)-[:MANEJA]->(v)
    """
    with get_driver().session() as s:
        s.run(cypher, cid=conductor_id, vid=vehiculo_id)


def incrementar_viajo_con(usuario_id: str, conductor_id: str) -> None:
    """Crea o incrementa la relación VIAJO_CON entre usuario y conductor."""
    cypher = """
        MATCH (u:Usuario {id: $uid}), (c:Conductor {id: $cid})
        MERGE (u)-[r:VIAJO_CON]->(c)
        ON CREATE SET r.cantidad_viajes = 1
        ON MATCH  SET r.cantidad_viajes = r.cantidad_viajes + 1
        SET r.ultimo_viaje_ts = datetime()
    """
    with get_driver().session() as s:
        s.run(cypher, uid=usuario_id, cid=conductor_id)


def coincidencias(min_viajes: int = 2) -> list[dict]:
    """Caso de uso 5: parejas usuario-conductor con N o más viajes en común."""
    cypher = """
        MATCH (u:Usuario)-[r:VIAJO_CON]->(c:Conductor)
        WHERE r.cantidad_viajes >= $n
        RETURN u.id AS pasajero_id, u.nombre AS pasajero,
               c.id AS conductor_id, c.nombre AS conductor,
               r.cantidad_viajes AS viajes
        ORDER BY viajes DESC
    """
    with get_driver().session() as s:
        return [dict(r) for r in s.run(cypher, n=min_viajes)]


def vehiculos_marca_y_patente_termina(marca: str, sufijo: str) -> int:
    """Caso de uso 6: cuántos vehículos de marca X tienen patente terminada en Y."""
    cypher = """
        MATCH (v:Vehiculo)
        WHERE v.marca = $marca AND v.placa ENDS WITH $sufijo
        RETURN count(v) AS c
    """
    with get_driver().session() as s:
        return s.run(cypher, marca=marca, sufijo=sufijo).single()["c"]
