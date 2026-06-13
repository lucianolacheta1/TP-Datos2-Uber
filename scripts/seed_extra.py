"""Carga ADITIVA para agrandar el sample size SIN alterar los 7 casos.

Se corre DESPUES de scripts.seed_data (que deja el dataset determinista de Meli).
Agrega entidades "neutras por construccion": cada caso de uso sigue dando el
MISMO resultado documentado.

  +13 conductores / +13 usuarios / +13 vehiculos
     - vehiculos: NUNCA Toyota y patente que NO termina en "D"  -> caso 6 intacto (3)
  +13 viajes FINALIZADOS:
     - pareja unica conductor<->usuario, 1 viaje c/u  -> caso 5 intacto (nadie llega a >=2)
     - duracion fija = 22 min                         -> caso 4 (promedio) sigue 22.00
     - recientes (finalizar pone ts = ahora)          -> caso 3 intacto (siguen solo Carolina/Roberto)
  +pagos TARJETA/EFECTIVO (NUNCA BILLETERA)           -> caso 2 intacto (BILLETERA sigue el minimo)
  +resenas rating 3 y 4 (NUNCA 5 ni <2)               -> caso 7 intacto; 1 U_A_C por usuario -> caso 1 intacto
  +20.000 pings GPS en Cassandra                      -> ningun caso lee ubicaciones_por_vehiculo

Uso (despues del seed determinista):
    python -m scripts.seed_data
    python -m scripts.seed_extra
"""
import decimal
import random
import uuid
from datetime import datetime, UTC, timedelta

from cassandra.concurrent import execute_concurrent_with_args

from src.config import validate
from src.services import (
    auth_service, vehiculo_service, viaje_service, pago_service, resena_service,
)
from src.repositories import vehiculo_repo
from src.db.cassandra import get_session
from src.utils.logger import logger

N_GPS = 20_000

CONDUCTORES_EXTRA = [
    ("ce01@m.com", "Gabriel Ferreyra",   "LIC-101"),
    ("ce02@m.com", "Romina Acosta",      "LIC-102"),
    ("ce03@m.com", "Hernán Ríos",        "LIC-103"),
    ("ce04@m.com", "Cecilia Paz",        "LIC-104"),
    ("ce05@m.com", "Maximiliano Bravo",  "LIC-105"),
    ("ce06@m.com", "Daniela Ponce",      "LIC-106"),
    ("ce07@m.com", "Federico Cabrera",   "LIC-107"),
    ("ce08@m.com", "Lucía Medina",       "LIC-108"),
    ("ce09@m.com", "Nicolás Herrera",    "LIC-109"),
    ("ce10@m.com", "Camila Sosa",        "LIC-110"),
    ("ce11@m.com", "Andrés Molina",      "LIC-111"),
    ("ce12@m.com", "Julieta Ramos",      "LIC-112"),
    ("ce13@m.com", "Tomás Vera",         "LIC-113"),
]

USUARIOS_EXTRA = [
    ("ue01@m.com", "Florencia Ibáñez"),
    ("ue02@m.com", "Joaquín Ledesma"),
    ("ue03@m.com", "Brenda Suárez"),
    ("ue04@m.com", "Emiliano Ortiz"),
    ("ue05@m.com", "Agustina Núñez"),
    ("ue06@m.com", "Santiago Rivas"),
    ("ue07@m.com", "Micaela Funes"),
    ("ue08@m.com", "Bruno Aguirre"),
    ("ue09@m.com", "Carla Benítez"),
    ("ue10@m.com", "Iván Maldonado"),
    ("ue11@m.com", "Rocío Cáceres"),
    ("ue12@m.com", "Lautaro Gómez"),
    ("ue13@m.com", "Paula Domínguez"),
]

# marcas/modelos para vehiculos extra. NUNCA Toyota -> caso 6 (Toyota patente D) intacto.
MARCAS_MODELOS = [
    ("Ford", "Focus"), ("Chevrolet", "Cruze"), ("Volkswagen", "Vento"),
    ("Renault", "Sandero"), ("Peugeot", "208"), ("Fiat", "Cronos"),
    ("Nissan", "Versa"), ("Honda", "Fit"), ("Hyundai", "HB20"),
    ("Kia", "Rio"), ("Citroën", "C3"), ("Jeep", "Renegade"), ("Suzuki", "Swift"),
]
COLORES = ["Blanco", "Negro", "Gris", "Rojo", "Azul", "Plata"]
# letras de patente que NO incluyen la "D" -> caso 6 intacto.
LETRAS_OK = "ABCEFGHJKLMNPQRSTUVWXYZ"

ORIGEN = {"lat": -34.6037, "lon": -58.3816, "direccion": "Microcentro"}
DESTINO = {"lat": -34.5876, "lon": -58.3934, "direccion": "Recoleta"}

# rango AMBA (igual que scripts/simulador_gps.py) para los pings GPS
LAT_MIN, LAT_MAX = -34.70, -34.52
LON_MIN, LON_MAX = -58.52, -58.33


def _placa(i: int) -> str:
    """Patente determinista que NUNCA termina en 'D' (LETRAS_OK no la contiene)."""
    a = LETRAS_OK[i % len(LETRAS_OK)]
    b = LETRAS_OK[(i * 3 + 1) % len(LETRAS_OK)]
    c = LETRAS_OK[(i * 7 + 2) % len(LETRAS_OK)]
    fin = LETRAS_OK[(i * 5 + 3) % len(LETRAS_OK)]
    return f"{a}{b}{c}{100 + i}{fin}"


def main() -> int:
    random.seed(123)
    validate()
    logger.info("=== Seed EXTRA (carga aditiva) iniciado ===")

    # 1. Conductores, usuarios y vehiculos extra
    conductores: list[tuple[str, str]] = []
    usuarios: list[tuple[str, str]] = []
    vehiculos: list[tuple[str, str, str]] = []

    for email, nombre, lic in CONDUCTORES_EXTRA:
        try:
            cid = auth_service.register_conductor(email, "demo1234", nombre, lic)
            conductores.append((cid, nombre))
        except Exception as e:
            logger.warning(f"Skip conductor {nombre}: {e}")

    for email, nombre in USUARIOS_EXTRA:
        try:
            uid = auth_service.register_usuario(email, "demo1234", nombre)
            usuarios.append((uid, nombre))
        except Exception as e:
            logger.warning(f"Skip usuario {nombre}: {e}")

    for i, (cid, cnombre) in enumerate(conductores):
        marca, modelo = MARCAS_MODELOS[i % len(MARCAS_MODELOS)]
        try:
            vid = vehiculo_service.registrar(
                cid, _placa(i), marca, modelo,
                2018 + (i % 6), random.choice(COLORES), "sedan",
            )
            vehiculos.append((vid, cid, cnombre))
        except Exception as e:
            logger.warning(f"Skip vehiculo de {cnombre}: {e}")

    logger.info(
        f"Extra: {len(conductores)} conductores, {len(usuarios)} usuarios, "
        f"{len(vehiculos)} vehiculos"
    )

    # 2. Un viaje FINALIZADO por conductor extra, con un usuario extra DISTINTO
    #    (pareja unica -> caso 5 intacto). Duracion 22 -> caso 4 intacto.
    n_viajes = min(len(vehiculos), len(usuarios))
    creados = 0
    for i in range(n_viajes):
        vid, cid, cnombre = vehiculos[i]
        uid, unombre = usuarios[i]
        try:
            viaje_id = viaje_service.solicitar(uid, cid, vid, ORIGEN, DESTINO)
            viaje_service.iniciar(viaje_id)
            viaje_service.finalizar(viaje_id, distancia_km=round(7.0 + i, 1), duracion_min=22)

            # Pago: alterna TARJETA / EFECTIVO (jamas BILLETERA_VIRTUAL -> caso 2 intacto)
            metodo = "TARJETA" if i % 2 == 0 else "EFECTIVO"
            monto = round(1200 + i * 80, 2)
            pago_service.procesar(
                viaje_id, monto, tarifa_base=500,
                tarifa_distancia=monto * 0.5, tarifa_tiempo=monto * 0.3,
                cargos_extra=monto * 0.05, metodo_pago=metodo,
            )

            # Resenas: rating 3 y 4 (NUNCA 5 ni <2 -> caso 7 intacto).
            # 1 sola U_A_C por usuario -> no desplaza a Juan/Maria/Carlos en caso 1.
            resena_service.crear(viaje_id, "U_A_C", uid, unombre, cid, cnombre, 4, "Todo bien")
            resena_service.crear(viaje_id, "C_A_U", cid, cnombre, uid, unombre, 3, "Normal")
            creados += 1
        except Exception as e:
            logger.warning(f"Skip viaje extra {i}: {e}")
    logger.info(f"Extra: {creados} viajes finalizados (con pago + 2 resenas c/u)")

    # 3. GPS masivo: N_GPS pings repartidos entre TODOS los vehiculos (reales + extra).
    #    Ningun caso de uso lee ubicaciones_por_vehiculo -> resultados intactos.
    todos_vids = [uuid.UUID(v["id"]) for v in vehiculo_repo.listar_todos()]
    if not todos_vids:
        logger.error("No hay vehiculos para cargar GPS.")
        return 1

    session = get_session()
    stmt = session.prepare(
        "INSERT INTO ubicaciones_por_vehiculo "
        "(vehiculo_id, ts, lat, lon, precision_m, viaje_id) VALUES (?, ?, ?, ?, ?, ?)"
    )
    ahora = datetime.now(UTC)
    ventana = 30 * 24 * 3600  # ultimos 30 dias en segundos
    args = []
    for _ in range(N_GPS):
        v = random.choice(todos_vids)
        ts = ahora - timedelta(
            seconds=random.randint(0, ventana),
            microseconds=random.randint(0, 999_999),
        )
        lat = decimal.Decimal(str(round(random.uniform(LAT_MIN, LAT_MAX), 6)))
        lon = decimal.Decimal(str(round(random.uniform(LON_MIN, LON_MAX), 6)))
        prec = round(random.uniform(3.0, 12.0), 1)
        args.append((v, ts, lat, lon, prec, None))

    logger.info(f"Insertando {N_GPS} pings GPS en Cassandra (concurrente)...")
    ok = 0
    for success, _res in execute_concurrent_with_args(
        session, stmt, args, concurrency=50, raise_on_first_error=False
    ):
        if success:
            ok += 1
    logger.info(f"GPS insertados OK: {ok}/{N_GPS}")

    print("\nSeed EXTRA completo (aditivo). Resumen de lo agregado:")
    print(f"  +Conductores: {len(conductores)}")
    print(f"  +Usuarios:    {len(usuarios)}")
    print(f"  +Vehiculos:   {len(vehiculos)}")
    print(f"  +Viajes:      {creados}  (duracion fija 22 min)")
    print(f"  +Pagos:       {creados}  (TARJETA/EFECTIVO, sin BILLETERA)")
    print(f"  +Resenas:     {2 * creados}  (rating 3 y 4)")
    print(f"  +GPS pings:   {ok}")
    print("\nLos 7 casos siguen dando el MISMO resultado documentado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
