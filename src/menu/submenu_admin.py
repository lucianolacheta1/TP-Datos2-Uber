"""Submenu de administracion: health check, reconciliacion, outbox, reset."""
import threading

from src.db import postgres, mongo, cassandra, neo4j_db, redis_db
from src.services import reconciliacion_service
from src.utils import outbox
from src.menu import formato

# Estado del simulador GPS (per-vehiculo, corre en un hilo controlado por un Event)
_sim_thread: threading.Thread | None = None
_sim_event = threading.Event()


def loop() -> None:
    while True:
        formato.subtitulo("Administración")
        print("1. Verificar conexiones a las 5 bases")
        print("2. Reconciliar Neo4j desde Mongo")
        print("3. Ver outbox (proyecciones fallidas)")
        print("4. Limpiar el outbox")
        print("5. Limpiar TODAS las bases (peligroso)")
        print("6. Iniciar simulador GPS")
        print("7. Detener simulador GPS")
        print("8. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _health_check()
        elif op == "2":
            _reconciliar()
        elif op == "3":
            _ver_outbox()
        elif op == "4":
            _limpiar_outbox()
        elif op == "5":
            _reset_dbs()
        elif op == "6":
            _iniciar_simulador()
        elif op == "7":
            _detener_simulador()
        elif op == "8":
            return
        else:
            formato.error("Opción inválida.")


def _health_check() -> None:
    bases = [
        ("Postgres   (Neon)",   postgres.check),
        ("MongoDB    (Atlas)",  mongo.check),
        ("Cassandra  (Astra)",  cassandra.check),
        ("Neo4j      (Aura)",   neo4j_db.check),
        ("Redis      (Cloud)",  redis_db.check),
    ]
    for nombre, fn in bases:
        ok = fn()
        if ok:
            formato.exito(f"{nombre}: OK")
        else:
            formato.error(f"{nombre}: FAIL")
    formato.pausa()


def _reconciliar() -> None:
    formato.info("Reconstruyendo aristas VIAJO_CON en Neo4j desde Mongo...")
    stats = reconciliacion_service.sync_neo4j_desde_mongo()
    formato.exito(
        f"Listo. Pares reconstruidos: {stats['pares_reconstruidos']}, "
        f"viajes procesados: {stats['viajes_procesados']}."
    )
    formato.pausa()


def _ver_outbox() -> None:
    stats = reconciliacion_service.procesar_outbox()
    formato.info(f"Outbox tiene {stats['pendientes']} entradas pendientes.")
    if stats["pendientes"] > 0:
        formato.tabla(stats["entradas"], columnas=["ts", "operation"])
    formato.pausa()


def _limpiar_outbox() -> None:
    if formato.confirmar("¿Seguro que querés limpiar el outbox?"):
        outbox.clear()
        formato.exito("Outbox limpio.")
    formato.pausa()


def _iniciar_simulador() -> None:
    global _sim_thread
    if _sim_event.is_set():
        formato.error("El simulador ya está corriendo.")
        formato.pausa()
        return
    vehiculo_id = formato.pedir_input("ID del vehículo a simular")
    from scripts import simulador_gps
    _sim_event.set()
    _sim_thread = threading.Thread(
        target=simulador_gps.correr,
        args=(vehiculo_id, 2, _sim_event),
        daemon=True, name="SimuladorGPS",
    )
    _sim_thread.start()
    formato.exito(f"Simulador GPS arrancado para {vehiculo_id} (cada 2s).")
    formato.pausa()


def _detener_simulador() -> None:
    if not _sim_event.is_set():
        formato.error("El simulador no está corriendo.")
        formato.pausa()
        return
    _sim_event.clear()
    if _sim_thread is not None:
        _sim_thread.join(timeout=5)
    formato.exito("Simulador GPS detenido.")
    formato.pausa()


def _reset_dbs() -> None:
    formato.error("ATENCIÓN: esto borra TODOS los datos de las 5 bases.")
    if not formato.confirmar('Escribí "s" para confirmar'):
        formato.info("Cancelado.")
        formato.pausa()
        return

    # Reusar la lógica de scripts/reset_all_dbs.py
    from scripts import reset_all_dbs
    reset_all_dbs.reset_postgres()
    reset_all_dbs.reset_mongo()
    reset_all_dbs.reset_cassandra()
    reset_all_dbs.reset_neo4j()
    reset_all_dbs.reset_redis()
    formato.exito("Todas las bases fueron limpiadas.")
    formato.info("Recordá correr `python -m scripts.init_mongo` para recrear índices.")
    formato.pausa()
