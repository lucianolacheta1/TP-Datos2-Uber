"""Seed de datos realista para la demo y testing manual.

Dataset DETERMINISTA que cubre los 7 casos con resultados EXACTOS y documentables
(sin azar en lo que afecta a cada caso):
- 10 usuarios, 5 conductores, 7 vehículos.
- 16 viajes finalizados (parejas controladas para el caso 5).
- 16 pagos (9 TARJETA / 5 EFECTIVO / 2 BILLETERA para el caso 2).
- 32 reseñas (ratings fijos para el caso 7, autores controlados para el caso 1).
- Distribución temporal fija para el caso 3 (Carolina y Roberto inactivos).

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


# ---- plan determinista del dataset (constantes de modulo, testeable sin DB) ----

# (idx_usuario, idx_conductor, dias_atras). Pensado para que los 7 casos den
# resultados EXACTOS y documentables. Ver el detalle del diseno en main().
PLAN_VIAJES: list[tuple[int, int, int]] = [
    (0, 0, 2), (0, 0, 5), (0, 0, 8), (0, 0, 11),   # Juan   <-> Ana Gomez (x4)
    (1, 1, 3), (1, 1, 6), (1, 1, 9),               # Maria  <-> Luis      (x3)
    (2, 2, 4), (2, 2, 7),                          # Carlos <-> Beatriz   (x2)
    (3, 0, 1),    # Ana Rodriguez <-> Ana Gomez
    (4, 1, 2),    # Pedro         <-> Luis
    (5, 2, 3),    # Laura         <-> Beatriz
    (6, 0, 5),    # Diego         <-> Ana Gomez
    (7, 1, 6),    # Sofia         <-> Luis
    (8, 2, 8),    # Martin        <-> Beatriz
    (9, 4, 60),   # Valentina     <-> Carolina (viejo) -> caso 3 inactivos
]
# Duraciones alternadas 20/24 -> promedio EXACTO 22.00 min (caso 4).
DURACIONES = [20 if i % 2 == 0 else 24 for i in range(len(PLAN_VIAJES))]
DISTANCIAS = [round(8.0 + (i % 5) * 2.5, 1) for i in range(len(PLAN_VIAJES))]
# Pagos: BILLETERA_VIRTUAL es el menos usado, 2 vs 5 vs 9 (caso 2).
METODOS = (["TARJETA"] * 9 + ["EFECTIVO"] * 5 + ["BILLETERA_VIRTUAL"] * 2)[:len(PLAN_VIAJES)]
# Ratings fijos: 6 resenas con rating 5 y 4 con rating 1 (caso 7).
# Por viaje hay una resena U_A_C (RATING_USER) y una C_A_U (RATING_COND).
RATING_USER = [5, 5, 5, 1, 1, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3, 4]
RATING_COND = [4, 3, 5, 5, 5, 1, 1, 4, 3, 4, 3, 4, 3, 4, 3, 4]


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

    # 2. Plan determinista (constantes de modulo: PLAN_VIAJES / DURACIONES / ...).
    # Logica del diseno:
    #  - Caso 5: cada pasajero (Juan/Maria/Carlos) viaja SIEMPRE con el mismo
    #    conductor -> esas 3 parejas son las unicas con >= 2 viajes.
    #  - Caso 1: por eso esos 3 lideran el top de resenadores; el relleno usa
    #    parejas unicas (1 viaje c/u) y no los desplaza.
    #  - Caso 3: Carolina viaja 1 vez hace 60 dias y Roberto nunca -> inactivos.
    plan_viajes = PLAN_VIAJES
    duraciones = DURACIONES
    distancias = DISTANCIAS

    # 3. Ejecutar el plan
    viajes_creados: list[tuple[str, int, int]] = []  # (viaje_id, idx_user, idx_cond)
    ahora = datetime.now(UTC)
    for i, (idx_user, idx_cond, dias_atras) in enumerate(plan_viajes):
        usuario = usuarios[idx_user]
        conductor = conductores[idx_cond]
        # Vehiculo del conductor: tomar el primero suyo
        vehiculo = next(v for v in vehiculos if v[1] == conductor[0])
        fecha_fin = ahora - timedelta(days=dias_atras, hours=(i % 12))
        viaje_id = _crear_viaje_finalizado(
            usuario, conductor, vehiculo, fecha_fin, duraciones[i], distancias[i],
        )
        viajes_creados.append((viaje_id, idx_user, idx_cond))
    logger.info(f"{len(viajes_creados)} viajes creados")

    # 4. Pagos DETERMINISTAS (caso 2): BILLETERA_VIRTUAL es el menos usado.
    #    16 viajes -> 9 TARJETA, 5 EFECTIVO, 2 BILLETERA_VIRTUAL.
    metodos = METODOS[:len(viajes_creados)]
    for i, ((viaje_id, _, _), metodo) in enumerate(zip(viajes_creados, metodos)):
        monto = round(1000 + (i % 8) * 350, 2)
        _crear_pago(viaje_id, monto, metodo)
    logger.info(f"{len(viajes_creados)} pagos creados")

    # 5. Resenas DETERMINISTAS.
    # Caso 7 (rating 5 o <2): EXACTAMENTE 6 resenas con rating 5 y 4 con rating 1.
    # Por viaje: una resena U_A_C (rating_user) y una C_A_U (rating_cond).
    rating_user = RATING_USER
    rating_cond = RATING_COND
    for i, (viaje_id, idx_user, idx_cond) in enumerate(viajes_creados):
        usuario = usuarios[idx_user]
        conductor = conductores[idx_cond]
        ru = rating_user[i % len(rating_user)]
        rc = rating_cond[i % len(rating_cond)]
        try:
            _crear_resena(viaje_id, usuario, conductor, "U_A_C", ru)
            _crear_resena(viaje_id, usuario, conductor, "C_A_U", rc)
        except Exception as e:
            logger.warning(f"No se pudo resenar viaje {viaje_id}: {e}")
    logger.info("Reseñas creadas")

    print("\nSeed completo. Resumen:")
    print(f"  Usuarios:     {len(usuarios)}")
    print(f"  Conductores:  {len(conductores)}")
    print(f"  Vehículos:    {len(vehiculos)}")
    print(f"  Viajes:       {len(viajes_creados)}")
    print(f"  Pagos:        {len(viajes_creados)}")
    print(f"  Reseñas:      {2 * len(viajes_creados)}")
    print("\nResultados esperados por caso de uso (deterministas con este seed):")
    print("  Caso 1 (top 3):            Juan Pérez (4), María García (3), Carlos López (2)")
    print("  Caso 2 (pago menos usado): BILLETERA_VIRTUAL (2 pagos; EFECTIVO 5, TARJETA 9)")
    print("  Caso 3 (inactivos):        Carolina Vega + Roberto Núñez")
    print("  Caso 4 (tiempo promedio):  22.00 min")
    print("  Caso 5 (coincidencias):    Juan-Ana (4), María-Luis (3), Carlos-Beatriz (2)")
    print("  Caso 6 (Toyota patente D): 3 vehículos")
    print("  Caso 7 (rating extremo):   10 reseñas (6 con rating 5, 4 con rating 1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
