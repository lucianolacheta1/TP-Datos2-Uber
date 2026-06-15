"""Test automatico end-to-end del sistema (reemplaza el test_automatico.py original).

Devuelve, en una sola corrida:
  [0] Estado de las conexiones a las 5 bases (Postgres, Mongo, Cassandra, Neo4j, Redis).
  [A] Flujo de negocio completo (registro -> viaje -> pago -> resena) via services.
  [B] Resultado de los 7 casos de uso.

POR QUE NO se maneja el menu por stdin (como el script original):
  - login/registro/admin usan getpass(): lee del TERMINAL, no de stdin -> no se
    puede alimentar la password por pipe de forma confiable.
  - el menu de operacion usa selecciones de LISTA generadas en runtime desde la DB
    -> no se pueden predecir las posiciones de antemano.
Por eso ejercita la MISMA logica que el menu llama por debajo (los services).

Los datos que crea son NEUTROS (no alteran los 7 casos): pareja unica de 1 viaje,
duracion 22, vehiculo no-Toyota, pago no-BILLETERA, resena rating 4.

Uso (desde cualquier carpeta):
    python -m scripts.test_automatico
    # o:  python scripts/test_automatico.py
"""
import os
import sys
import time
import traceback

# Permite correrlo como script suelto (agrega la raiz del proyecto al path)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import validate
from src.db import postgres, mongo, cassandra, neo4j_db, redis_db
from src.services import (
    auth_service, vehiculo_service, viaje_service, pago_service, resena_service,
)
from src.casos_uso import (
    caso_01_top_resenadores, caso_02_metodo_pago, caso_03_conductores_inactivos,
    caso_04_promedio_viajes, caso_05_coincidencias, caso_06_toyota_patente_d,
    caso_07_resenas_extremas,
)
from src.repositories import cache_repo

_oks = 0
_fallos = 0


def check(nombre: str, cond: bool, detalle: str = "") -> None:
    global _oks, _fallos
    if cond:
        _oks += 1
        print(f"  [OK]    {nombre} {detalle}")
    else:
        _fallos += 1
        print(f"  [FALLO] {nombre} {detalle}")


def _estado_conexiones() -> None:
    """[0] Verifica las 5 conexiones (igual que el health-check del menu admin)."""
    print("[0] Estado de las conexiones a las bases")
    bases = [
        ("Postgres  (Neon)",   postgres.check),
        ("MongoDB   (Atlas)",  mongo.check),
        ("Cassandra (Astra)",  cassandra.check),
        ("Neo4j     (Aura)",   neo4j_db.check),
        ("Redis     (Cloud)",  redis_db.check),
    ]
    for nombre, fn in bases:
        try:
            ok = fn()
        except Exception as e:
            ok = False
            print(f"  [FALLO] {nombre}: {e}")
            global _fallos
            _fallos += 1
            continue
        check(f"{nombre}: conexion", ok)


def main() -> int:
    global _fallos
    validate()
    stamp = int(time.time())
    pwd = "demo1234"
    print("=== TEST AUTOMATICO E2E ===")
    print(f"stamp={stamp}\n")

    # ---------- [0] Conexiones ----------
    _estado_conexiones()

    # ---------- [A] Flujo de negocio via services ----------
    print("\n[A] Flujo de negocio (registro -> viaje -> pago -> resena)")
    try:
        u_email = f"smoke_u_{stamp}@test.com"
        c_email = f"smoke_c_{stamp}@test.com"

        uid = auth_service.register_usuario(u_email, pwd, "Smoke Usuario")
        check("register_usuario", bool(uid), f"uid={uid[:8]}")

        cid = auth_service.register_conductor(c_email, pwd, "Smoke Conductor", f"LIC-SMK-{stamp}")
        check("register_conductor", bool(cid), f"cid={cid[:8]}")

        token = auth_service.login(u_email, pwd, "USUARIO")
        check("login devuelve token", bool(token))

        data = auth_service.validate_session(token)
        check("validate_session", data is not None and data.get("user_id") == uid,
              f"tipo={data and data.get('tipo')}")

        vid = vehiculo_service.registrar(cid, f"SMK{stamp % 100000}A", "Ford", "Focus",
                                         2021, "Gris", "sedan")
        check("registrar vehiculo (no-Toyota)", bool(vid))

        origen = {"lat": -34.60, "lon": -58.38, "direccion": "Centro"}
        destino = {"lat": -34.58, "lon": -58.42, "direccion": "Palermo"}
        viaje_id = viaje_service.solicitar(uid, cid, vid, origen, destino)
        check("solicitar viaje", bool(viaje_id), f"viaje={viaje_id[:8]}")

        check("iniciar viaje", viaje_service.iniciar(viaje_id) is True)

        viaje_service.finalizar(viaje_id, 8.0, 22)  # duracion 22 -> no mueve el caso 4
        check("finalizar viaje (proyecta a Cassandra/Neo4j/Redis)", True, "(duracion 22)")

        pago_service.procesar(
            viaje_id, 1500.0, tarifa_base=500, tarifa_distancia=750,
            tarifa_tiempo=450, cargos_extra=0, metodo_pago="EFECTIVO",  # no-BILLETERA
        )
        check("procesar pago (EFECTIVO)", True)

        resena_service.crear(
            viaje_id, "U_A_C", uid, "Smoke Usuario", cid, "Smoke Conductor",
            4, "Smoke test",  # rating 4 -> no toca el caso 7
        )
        check("crear resena (rating 4)", True)
    except Exception as e:
        _fallos += 1
        print(f"  [FALLO] excepcion en el flujo: {e}")
        traceback.print_exc()

    # ---------- [B] 7 casos de uso ----------
    print("\n[B] Los 7 casos de uso")
    for k in ("top3_resenadores", "viajes_promedio"):
        try:
            cache_repo.invalidar(k)  # leer la verdad de las bases, no cache
        except Exception:
            pass

    try:
        top = caso_01_top_resenadores.ejecutar()
        print(f"  Caso 1 top3: {[(r.get('nombre'), r.get('cantidad')) for r in top]}")
        check("Caso 1: lider = Juan Perez", bool(top) and top[0].get("nombre") == "Juan Pérez")

        m = caso_02_metodo_pago.ejecutar()
        print(f"  Caso 2: {m}")
        check("Caso 2: BILLETERA_VIRTUAL", m == "BILLETERA_VIRTUAL")

        inact = caso_03_conductores_inactivos.ejecutar()
        nombres_in = [x.get("nombre") for x in inact]
        print(f"  Caso 3 inactivos: {nombres_in}")
        check("Caso 3: incluye Carolina y Roberto",
              any("Carolina" in (n or "") for n in nombres_in)
              and any("Roberto" in (n or "") for n in nombres_in),
              "(puede traer ruido de pruebas manuales)")

        prom = caso_04_promedio_viajes.ejecutar()
        print(f"  Caso 4: {prom:.2f} min")
        check("Caso 4: 22.00 min", abs(prom - 22.0) < 0.01)

        co = caso_05_coincidencias.ejecutar()
        print(f"  Caso 5: {[(r.get('pasajero'), r.get('conductor'), r.get('viajes')) for r in co]}")
        check("Caso 5: 3 parejas con >=2 viajes", len(co) == 3)

        c6 = caso_06_toyota_patente_d.ejecutar()
        print(f"  Caso 6: {c6}")
        check("Caso 6: 3 Toyota patente D", c6 == 3)

        c7 = caso_07_resenas_extremas.ejecutar()
        print(f"  Caso 7: {len(c7)} resenas extremas")
        check("Caso 7: 10 resenas extremas", len(c7) == 10,
              "(puede variar si hubo pruebas manuales)")
    except Exception as e:
        _fallos += 1
        print(f"  [FALLO] excepcion en los casos: {e}")
        traceback.print_exc()

    print(f"\n=== RESUMEN: {_oks} OK, {_fallos} FALLO ===")
    return 1 if _fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
