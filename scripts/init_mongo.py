"""Crea los índices necesarios en las colecciones de Mongo."""
from src.db.mongo import get_db
from src.utils.logger import logger


def main():
    db = get_db()

    # viajes
    db.viajes.create_index([("usuario_id", 1)])
    db.viajes.create_index([("conductor_id", 1)])
    db.viajes.create_index([("estado", 1), ("ts_inicio", -1)])
    db.viajes.create_index([("ts_fin", -1)])

    # pagos
    db.pagos.create_index([("viaje_id", 1)])
    db.pagos.create_index([("metodo_pago", 1)])
    db.pagos.create_index([("estado", 1), ("timestamp", -1)])

    # resenas
    db.resenas.create_index([("autor.id", 1)])
    db.resenas.create_index([("destinatario.id", 1)])
    db.resenas.create_index([("tipo", 1), ("rating", 1)])
    db.resenas.create_index([("rating", 1)])

    # login_history
    db.login_history.create_index([("usuario_id", 1), ("timestamp", -1)])
    db.login_history.create_index([("evento", 1)])

    logger.info("Índices creados en MongoDB")
    print("OK: índices creados en MongoDB")


if __name__ == "__main__":
    main()
