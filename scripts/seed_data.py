"""Seed de datos realista para la demo y testing manual.

Genera un dataset coherente que cubre los 7 casos de uso del enunciado:
- 10 usuarios, 5 conductores, 7 vehículos.
- ~50 viajes finalizados (con coincidencias específicas para el caso 5).
- ~50 pagos (distribución de métodos para el caso 2).
- ~100 reseñas (ratings distribuidos para el caso 7, autores variados para el caso 1).
- Distribución temporal para el caso 3 (algunos conductores inactivos).

Uso:
    python -m scripts.seed_data
"""
import random
import uuid
from datetime import datetime, UTC, timedelta

from src.config import validate
from src.services import (
    auth_service, vehiculo_service,
    viaje_service, pago_service, resena_service,
)
from src.utils.logger import logger

# ---- datos base ----

USUARIOS = [
    ("juan@m.com",     "Juan Pérez"),
    ("maria@m.com",    "María García"),
    ("carlos@m.com",   "Carlos López"),
    ("ana@m.com",      "Ana Rodríguez"),
    ("pedro@m.com",    "Pedro Martínez"),
    ("laura@m.com",    "Laura Fernández"),
    ("diego@m.com",    "Diego Sánchez"),
    ("sofia@m.com",    "Sofía Romero"),
    ("martin@m.com",   "Martín Díaz"),
    ("valentina@m.com","Valentina Torres"),
]

CONDUCTORES = [
    # (email, nombre, licencia)
    ("anag@m.com",     "Ana Gómez",       "LIC-001"),
    ("luis@m.com",     "Luis Castro",     "LIC-002"),
    ("beatriz@m.com",  "Beatriz Silva",   "LIC-003"),
    ("roberto@m.com",  "Roberto Núñez",   "LIC-004"),
    ("carolina@m.com", "Carolina Vega",   "LIC-005"),
]

VEHICULOS = [
    # (idx_conductor, placa, marca, modelo, anio, color, tipo)
    (0, "ABC123D", "Toyota",     "Corolla", 2020, "Blanco", "sedan"),
    (0, "XYZ888D", "Toyota",     "Hilux",   2021, "Negro",  "pickup"),
    (1, "TOY222D", "Toyota",     "Etios",   2019, "Gris",   "sedan"),
    (1, "HND111A", "Honda",      "Civic",   2022, "Azul",   "sedan"),
    (2, "FRD555X", "Ford",       "Focus",   2018, "Rojo",   "sedan"),
    (3, "VWA444B", "Volkswagen", "Gol",     2020, "Blanco", "sedan"),
    (4, "RNT666D", "Renault",    "Sandero", 2019, "Plata",  "sedan"),
]

LUGARES = [
    ({"lat": -34.6087, "lon": -58.3716, "direccion": "Microcentro"}, {"lat": -34.5876, "lon": -58.3934, "direccion": "Recoleta"}),
    ({"lat": -34.5778, "lon": -58.4226, "direccion": "Palermo"},     {"lat": -34.5631, "lon": -58.4587, "direccion": "Belgrano"}),
    ({"lat": -34.6443, "lon": -58.4116, "direccion": "Caballito"},   {"lat": -34.6037, "lon": -58.3816, "direccion": "Monserrat"}),
    ({"lat": -34.5499, "lon": -58.4632, "direccion": "Núñez"},       {"lat": -34.5878, "lon": -58.4174, "direccion": "Las Heras"}),
    ({"lat": -34.6178, "lon": -58.3645, "direccion": "Puerto Madero"}, {"lat": -34.6010, "lon": -58.3819, "direccion": "Once"}),
]

COMENTARIOS_5 = ["Excelente viaje", "Muy amable y puntual", "10/10 lo recomiendo", "Perfecto, sin quejas", "Auto impecable"]
COMENTARIOS_4 = ["Buen viaje", "Todo bien", "Sin novedades", "Cumplió", "Conforme"]
COMENTARIOS_3 = ["Aceptable", "Normal", "Ni bueno ni malo"]
COMENTARIOS_1 = ["Muy mal trato", "Llegó tarde y de mal humor", "No vuelvo a usarlo"]


# ---- helpers ----

def _crear_usuarios(usuarios_data: list) -> list[tuple[str, str]]:
    """Registra usuarios. Devuelve [(id, nombre), ...]."""
    out = []
    for email, nombre in usuarios_data:
        try:
            uid = auth_service.register_usuario(email, "demo1234", nombre)
            out.append((uid, nombre))
            logger.info(f"Usuario creado: {nombre}")
        except Exception as e:
            logger.warning(f"Skipping {nombre}: {e}")
    return out


def _crear_conductores(conductores_data: list) -> list[tuple[str, str]]:
    out = []
    for email, nombre, licencia in conductores_data:
        try:
            cid = auth_service.register_conductor(email, "demo1234", nombre, licencia)
            out.append((cid, nombre))
            logger.info(f"Conductor creado: {nombre}")
        except Exception as e:
            logger.warning(f"Skipping {nombre}: {e}")
    return out


def _crear_vehiculos(vehiculos_data: list, conductores: list) -> list[tuple[str, str, str]]:
    """Devuelve [(vehiculo_id, conductor_id, conductor_nombre), ...]."""
    out = []
    for idx_cond, placa, marca, modelo, anio, color, tipo in vehiculos_data:
        cid, cnombre = conductores[idx_cond]
        try:
            vid = vehiculo_service.registrar(cid, placa, marca, modelo, anio, color, tipo)
            out.append((vid, cid, cnombre))
            logger.info(f"Vehículo {placa} ({marca}) creado para {cnombre}")
        except Exception as e:
            logger.warning(f"Skipping vehículo {placa}: {e}")
    return out


def _crear_viaje_finalizado(
    usuario: tuple[str, str],
    conductor: tuple[str, str],
    vehiculo: tuple[str, str, str],
    fecha_fin: datetime,
    duracion_min: int,
    distancia_km: float,
) -> str:
    """Crea un viaje y lo finaliza con la fecha indicada."""
    uid, _ = usuario
    cid, _ = conductor
    vid, _, _ = vehiculo
    origen, destino = random.choice(LUGARES)

    viaje_id = viaje_service.solicitar(uid, cid, vid, origen, destino)
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, distancia_km, duracion_min)

    # Sobreescribir ts_fin manualmente para simular fechas pasadas (caso 3).
    # OJO: viaje_id es el ObjectId como str; hay que convertirlo para matchear el _id.
    from bson import ObjectId
    from src.db.mongo import get_db
    get_db().viajes.update_one(
        {"_id": ObjectId(viaje_id)},
        {"$set": {"ts_fin": fecha_fin}},
    )

    # El caso 3 (conductores inactivos) lee de Cassandra (ultimo_viaje_ts), que
    # finalizar() setea a "ahora". Backdateamos también ahí para que la fecha
    # simulada tenga efecto; si no, todos los conductores quedan "activos".
    import uuid as _uuid
    from src.repositories import actividad_repo
    actividad_repo.upsert_ultima(
        _uuid.UUID(cid), fecha_fin, _uuid.UUID(viaje_id.rjust(32, "0"))
    )
    return viaje_id


def _crear_pago(viaje_id: str, monto: float, metodo: str) -> None:
    pago_service.procesar(
        viaje_id, monto,
        tarifa_base=500,
        tarifa_distancia=monto * 0.5,
        tarifa_tiempo=monto * 0.3,
        cargos_extra=monto * 0.05,
        metodo_pago=metodo,
    )


def _crear_resena(viaje_id: str, usuario: tuple, conductor: tuple,
                  tipo: str, rating: int) -> None:
    if tipo == "U_A_C":
        autor_id, autor_nombre = usuario
        dest_id, dest_nombre = conductor
    else:
        autor_id, autor_nombre = conductor
        dest_id, dest_nombre = usuario

    comentario = {
        5: random.choice(COMENTARIOS_5),
        4: random.choice(COMENTARIOS_4),
        3: random.choice(COMENTARIOS_3),
        1: random.choice(COMENTARIOS_1),
    }.get(rating, "Sin comentario")

    resena_service.crear(
        viaje_id, tipo,
        autor_id, autor_nombre,
        dest_id, dest_nombre,
        rating, comentario,
    )


# ---- main ----

def main() -> int:
    random.seed(42)  # reproducible
    validate()

    logger.info("=== Seed iniciado ===")

    # 1. Usuarios y conductores
    usuarios = _crear_usuarios(USUARIOS)
    conductores = _crear_conductores(CONDUCTORES)
    vehiculos = _crear_vehiculos(VEHICULOS, conductores)

    if not usuarios or not conductores or not vehiculos:
        logger.error("No se pudieron crear entidades base. Abortando.")
        return 1

    # 2. Construir el plan de viajes
    # Estructura: lista de (idx_usuario, idx_conductor, dias_atras)
    plan_viajes: list[tuple[int, int, int]] = []

    # Coincidencias para caso 5
    for _ in range(4):  # Juan ↔ Ana Gómez (idx 0 user, idx 0 cond)
        plan_viajes.append((0, 0, random.randint(0, 20)))
    for _ in range(3):  # María ↔ Luis Castro (idx 1, idx 1)
        plan_viajes.append((1, 1, random.randint(0, 20)))
    for _ in range(2):  # Carlos ↔ Beatriz Silva (idx 2, idx 2)
        plan_viajes.append((2, 2, random.randint(0, 20)))

    # Resto de viajes (~41), excluyendo Carolina Vega (idx 4 cond) y Roberto Núñez (idx 3)
    # como conductores recientes
    conductores_activos = [0, 1, 2]  # Ana, Luis, Beatriz
    for _ in range(40):
        idx_user = random.randint(0, len(usuarios) - 1)
        idx_cond = random.choice(conductores_activos)
        # Evitar duplicar coincidencias (no queremos más Juan-Ana)
        if (idx_user, idx_cond) in [(0, 0), (1, 1), (2, 2)]:
            continue
        plan_viajes.append((idx_user, idx_cond, random.randint(0, 25)))

    # 1 viaje viejo de Carolina (idx 4 cond): hace 60 días → caso 3 la marca inactiva
    plan_viajes.append((5, 4, 60))
    # Roberto (idx 3) no aparece nunca → también inactivo

    # 3. Ejecutar el plan
    viajes_creados: list[tuple[str, int, int]] = []  # (viaje_id, idx_user, idx_cond)
    ahora = datetime.now(UTC)
    for idx_user, idx_cond, dias_atras in plan_viajes:
        usuario = usuarios[idx_user]
        conductor = conductores[idx_cond]
        # Vehículo del conductor: tomar el primero suyo
        vehiculo = next(v for v in vehiculos if v[1] == conductor[0])
        duracion = random.randint(10, 45)
        distancia = round(random.uniform(2.0, 25.0), 1)
        fecha_fin = ahora - timedelta(days=dias_atras, hours=random.randint(0, 23))
        viaje_id = _crear_viaje_finalizado(
            usuario, conductor, vehiculo, fecha_fin, duracion, distancia,
        )
        viajes_creados.append((viaje_id, idx_user, idx_cond))
    logger.info(f"{len(viajes_creados)} viajes creados")

    # 4. Pagos con distribución 30/15/5 (TARJETA/EFECTIVO/BILLETERA)
    metodos = ["TARJETA"] * 30 + ["EFECTIVO"] * 15 + ["BILLETERA_VIRTUAL"] * 5
    random.shuffle(metodos)
    metodos = metodos[:len(viajes_creados)]
    for (viaje_id, _, _), metodo in zip(viajes_creados, metodos):
        monto = round(random.uniform(800, 5000), 2)
        _crear_pago(viaje_id, monto, metodo)
    logger.info(f"{len(viajes_creados)} pagos creados")

    # 5. Reseñas con distribución de ratings
    # Caso 7: queremos ~5 con rating 5, ~3 con rating 1, resto 3-4.
    ratings_pool = [5] * 5 + [1] * 3 + [4] * 20 + [3] * 22
    random.shuffle(ratings_pool)
    for i, (viaje_id, idx_user, idx_cond) in enumerate(viajes_creados):
        usuario = usuarios[idx_user]
        conductor = conductores[idx_cond]
        rating_user = ratings_pool[i % len(ratings_pool)]
        rating_cond = ratings_pool[(i + 7) % len(ratings_pool)]
        try:
            _crear_resena(viaje_id, usuario, conductor, "U_A_C", rating_user)
            _crear_resena(viaje_id, usuario, conductor, "C_A_U", rating_cond)
        except Exception as e:
            logger.warning(f"No se pudo reseñar viaje {viaje_id}: {e}")
    logger.info("Reseñas creadas")

    print("\nSeed completo. Resumen:")
    print(f"  Usuarios:     {len(usuarios)}")
    print(f"  Conductores:  {len(conductores)}")
    print(f"  Vehículos:    {len(vehiculos)}")
    print(f"  Viajes:       {len(viajes_creados)}")
    print(f"  Pagos:        {len(viajes_creados)}")
    print(f"  Reseñas:      ~{2 * len(viajes_creados)}")
    print("\nResultados esperados por caso de uso:")
    print("  Caso 1 (top 3):           Juan, María y Carlos")
    print("  Caso 2 (pago menos usado): BILLETERA_VIRTUAL")
    print("  Caso 3 (inactivos):       Carolina Vega + Roberto Núñez")
    print("  Caso 4 (tiempo promedio): ~22 min")
    print("  Caso 5 (coincidencias):   Juan-Ana(4), María-Luis(3), Carlos-Beatriz(2)")
    print("  Caso 6 (Toyota patente D): 3 vehículos")
    print("  Caso 7 (rating extremo):  ~10 reseñas (5 con rating=5, 3 con rating=1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
