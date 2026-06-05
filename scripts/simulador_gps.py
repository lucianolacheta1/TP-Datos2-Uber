"""
scripts/simulador_gps.py
-------------------------
Simulador de coordenadas GPS para el demo de la presentación.

Genera coordenadas aleatorias dentro del AMBA (área de Buenos Aires)
y las reporta periódicamente a través de ubicacion_service, que a su vez:
  -> escribe en Cassandra (historial completo)
  -> actualiza Redis (última posición, TTL 30s)

Modos de uso:
1. Desde el submenú Admin: simulador_gps.correr(vehiculo_id, intervalo_seg, evento_parada)
   El menú pasa un threading.Event para detenerlo.
2. Standalone: python -m scripts.simulador_gps --vehiculo <id> [--intervalo 2] [--pasos 30]
3. Multi-vehículo (seed): simulador_gps.simular_varios(lista_de_ids, intervalo_seg, cantidad_pasos)

(Autoría original: Joana / jfanarasanchez. Integrado al backend del equipo.)
"""

import argparse
import random
import time
import threading
from datetime import datetime

from src.utils.logger import logger

# Area geografica de simulacion: AMBA (bounding box aproximado)
LAT_MIN, LAT_MAX = -34.70, -34.52   # sur a norte
LON_MIN, LON_MAX = -58.52, -58.33   # oeste a este

# Variacion maxima por paso (simula movimiento continuo, no teleportacion)
DELTA_LAT = 0.002   # ~220 m por paso
DELTA_LON = 0.002   # ~170 m por paso


def correr(
    vehiculo_id: str,
    intervalo_seg: int = 2,
    evento_parada: threading.Event | None = None,
    viaje_id: str | None = None,
) -> None:
    """Loop de simulacion para UN vehiculo. Disenado para correr en un hilo.

    evento_parada: threading.Event; corre MIENTRAS esta set(), termina al .clear().
    Si es None, corre indefinidamente hasta KeyboardInterrupt.
    """
    from src.services import ubicacion_service

    lat, lon = _posicion_inicial_aleatoria()
    pasos = 0
    logger.info(
        "[GPS] Iniciando simulador: vehiculo=%s, intervalo=%ds, viaje=%s",
        vehiculo_id, intervalo_seg, viaje_id or "libre",
    )
    try:
        while True:
            if evento_parada is not None and not evento_parada.is_set():
                logger.info("[GPS] Senal de parada recibida. Terminando simulador.")
                break

            lat, lon = _siguiente_posicion(lat, lon)
            ts = datetime.utcnow()
            try:
                ubicacion_service.reportar(
                    vehiculo_id=vehiculo_id, lat=lat, lon=lon, viaje_id=viaje_id,
                )
                pasos += 1
                logger.debug(
                    "[GPS] paso=%d vehiculo=%s lat=%.6f lon=%.6f ts=%s",
                    pasos, vehiculo_id, lat, lon, ts.strftime("%H:%M:%S"),
                )
                if evento_parada is None:
                    print(f"\r  [GPS] Paso {pasos:>4}  ({lat:.6f}, {lon:.6f})  {ts.strftime('%H:%M:%S')}",
                          end="", flush=True)
            except Exception as e:
                logger.error("[GPS] Error al reportar ubicacion: %s", e)

            time.sleep(intervalo_seg)
    except KeyboardInterrupt:
        print()
        logger.info("[GPS] Simulador detenido por KeyboardInterrupt.")
    finally:
        logger.info("[GPS] Simulador finalizado. Total de pasos: %d", pasos)


def simular_varios(
    vehiculo_ids: list[str],
    intervalo_seg: int = 2,
    cantidad_pasos: int = 20,
) -> None:
    """Simula GPS para multiples vehiculos en paralelo (cantidad fija de pasos)."""
    from src.services import ubicacion_service

    def _worker(vid: str) -> None:
        lat, lon = _posicion_inicial_aleatoria()
        for paso in range(cantidad_pasos):
            lat, lon = _siguiente_posicion(lat, lon)
            try:
                ubicacion_service.reportar(vehiculo_id=vid, lat=lat, lon=lon)
                logger.debug("[GPS-seed] vehiculo=%s paso=%d", vid, paso + 1)
            except Exception as e:
                logger.error("[GPS-seed] vehiculo=%s error: %s", vid, e)
            time.sleep(intervalo_seg)
        logger.info("[GPS-seed] vehiculo=%s: %d pasos completados.", vid, cantidad_pasos)

    hilos = [
        threading.Thread(target=_worker, args=(vid,), daemon=True, name=f"GPS-{vid[:8]}")
        for vid in vehiculo_ids
    ]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    logger.info("[GPS-seed] Simulacion multi-vehiculo finalizada.")


def _posicion_inicial_aleatoria() -> tuple[float, float]:
    return random.uniform(LAT_MIN, LAT_MAX), random.uniform(LON_MIN, LON_MAX)


def _siguiente_posicion(lat: float, lon: float) -> tuple[float, float]:
    nueva_lat = max(LAT_MIN, min(LAT_MAX, lat + random.uniform(-DELTA_LAT, DELTA_LAT)))
    nueva_lon = max(LON_MIN, min(LON_MAX, lon + random.uniform(-DELTA_LON, DELTA_LON)))
    return nueva_lat, nueva_lon


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="Simulador GPS para el TP Uber")
    parser.add_argument("--vehiculo", required=True, help="UUID del vehiculo")
    parser.add_argument("--intervalo", type=int, default=2, help="Segundos entre reportes (default: 2)")
    parser.add_argument("--pasos", type=int, default=0, help="Cantidad de pasos (0 = infinito)")
    parser.add_argument("--viaje", default=None, help="UUID del viaje activo (opcional)")
    args = parser.parse_args()

    print(f"\n  Simulador GPS - vehiculo: {args.vehiculo}")
    print(f"  Intervalo: {args.intervalo}s  |  Pasos: {'infinito' if args.pasos == 0 else args.pasos}")
    print("  Ctrl+C para detener.\n")

    if args.pasos == 0:
        correr(vehiculo_id=args.vehiculo, intervalo_seg=args.intervalo, evento_parada=None, viaje_id=args.viaje)
    else:
        simular_varios(vehiculo_ids=[args.vehiculo], intervalo_seg=args.intervalo, cantidad_pasos=args.pasos)
        print()
