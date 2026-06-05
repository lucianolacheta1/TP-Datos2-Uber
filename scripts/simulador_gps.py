"""Simulador de GPS: reporta posiciones aleatorias para los vehiculos en background.

Uso standalone:
    python -m scripts.simulador_gps

Uso programatico (ej. desde el menu admin):
    from scripts.simulador_gps import iniciar_simulador, detener_simulador
    iniciar_simulador()
    ...
    detener_simulador()

El thread reporta una posicion aleatoria cerca de CABA para cada vehiculo
registrado en Postgres, cada INTERVALO_SEG segundos.
"""
import random
import signal
import sys
import threading
import time

from src.config import validate
from src.repositories import vehiculo_repo
from src.services import ubicacion_service
from src.utils.logger import logger

INTERVALO_SEG = 2.0
# Centro CABA y un margen aleatorio
CENTRO_LAT, CENTRO_LON = -34.6037, -58.3816
MARGEN = 0.15

_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _loop(intervalo: float) -> None:
    """Loop del simulador, corre hasta que _stop_event se setea."""
    while not _stop_event.is_set():
        vehiculos = vehiculo_repo.listar_todos()
        if not vehiculos:
            logger.info("Simulador GPS: no hay vehículos registrados")
        for v in vehiculos:
            lat = CENTRO_LAT + random.uniform(-MARGEN, MARGEN)
            lon = CENTRO_LON + random.uniform(-MARGEN, MARGEN)
            try:
                ubicacion_service.reportar(v["id"], lat, lon)
            except Exception as e:
                logger.warning(f"Reporte GPS falló para {v['id']}: {e}")
        _stop_event.wait(intervalo)


def iniciar_simulador(intervalo: float = INTERVALO_SEG) -> None:
    """Inicia el simulador en un thread daemon. Idempotente."""
    global _thread
    if _thread is not None and _thread.is_alive():
        logger.info("Simulador GPS ya está corriendo")
        return
    _stop_event.clear()
    _thread = threading.Thread(target=_loop, args=(intervalo,), daemon=True)
    _thread.start()
    logger.info(f"Simulador GPS arrancado (intervalo={intervalo}s)")


def detener_simulador() -> None:
    """Frena el simulador limpiamente."""
    _stop_event.set()
    if _thread is not None:
        _thread.join(timeout=5)
    logger.info("Simulador GPS detenido")


def main() -> int:
    validate()
    iniciar_simulador()

    def _sigint(_signum, _frame):
        print("\nDeteniendo simulador...")
        detener_simulador()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint)
    print("Simulador GPS corriendo. Ctrl-C para detener.")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
