"""Demo automatica del flujo completo del TP, sin interaccion manual.

Util como fallback durante la presentacion si el menu interactivo se traba.

Uso:
    python -m scripts.demo_automatico

Cada paso imprime una narracion y pausa unos segundos antes del siguiente,
asi el profesor puede mirar lo que pasa en las ventanas de las bases.
"""
import os
import time
import uuid

from src.config import validate
from src.services import (
    auth_service, vehiculo_service,
    viaje_service, pago_service, resena_service, ubicacion_service,
)
from src.casos_uso import (
    caso_01_top_resenadores, caso_02_metodo_pago,
    caso_03_conductores_inactivos, caso_04_promedio_viajes,
    caso_05_coincidencias, caso_06_toyota_patente_d,
    caso_07_resenas_extremas,
)

PAUSA = int(os.environ.get("DEMO_PAUSA", "4"))  # segundos entre pasos (DEMO_PAUSA=0 = rapido)


def _narrar(mensaje: str) -> None:
    print(f"\n{'-' * 60}")
    print(f"  {mensaje}")
    print(f"{'-' * 60}\n")
    time.sleep(PAUSA)


def main() -> int:
    validate()

    # Sufijos únicos para no colisionar con datos previos
    suf = uuid.uuid4().hex[:6]

    _narrar(f"Paso 1: Registrar usuario Diego (sufijo {suf})")
    print(f"  Email: diego_{suf}@m.com")
    uid = auth_service.register_usuario(f"diego_{suf}@m.com", "demo", f"Diego {suf}")
    print(f"  Usuario id: {uid}")
    print("  Verificar en Postgres (tabla usuario) y Neo4j (nodo Usuario).")

    _narrar(f"Paso 2: Registrar conductor Ana (sufijo {suf})")
    cid = auth_service.register_conductor(
        f"ana_{suf}@m.com", "demo", f"Ana {suf}", f"LIC-{suf}",
    )
    print(f"  Conductor id: {cid}")
    print("  Verificar en Postgres (tabla conductor) y Neo4j (nodo Conductor).")

    _narrar("Paso 3: Login del usuario -> genera sesion Redis con TTL 600s")
    token = auth_service.login(f"diego_{suf}@m.com", "demo", "USUARIO")
    print(f"  Token: {token[:20]}...")
    print("  Verificar en Redis (clave session:...) y Mongo (login_history).")

    _narrar("Paso 4: Registrar un vehiculo Toyota Corolla con patente terminada en D")
    vid = vehiculo_service.registrar(
        cid, f"ZZZ{suf[:3].upper()}D", "Toyota", "Corolla", 2022, "Blanco", "sedan",
    )
    print(f"  Vehiculo id: {vid}")
    print("  Verificar en Postgres (tabla vehiculo) y Neo4j (Conductor)-[:MANEJA]->(Vehiculo).")

    _narrar("Paso 5: Solicitar un viaje (Mongo con snapshots desde Postgres)")
    origen = {"lat": -34.6037, "lon": -58.3816, "direccion": "Microcentro"}
    destino = {"lat": -34.5876, "lon": -58.3934, "direccion": "Recoleta"}
    viaje_id = viaje_service.solicitar(uid, cid, vid, origen, destino)
    print(f"  Viaje id: {viaje_id}")
    print("  Verificar en Mongo (coleccion viajes) - notar el snapshot del usuario y conductor.")

    _narrar("Paso 6: Iniciar el viaje y reportar 3 posiciones GPS")
    viaje_service.iniciar(viaje_id)
    for i, (lat, lon) in enumerate([(-34.6037, -58.3816), (-34.5955, -58.3870), (-34.5876, -58.3934)]):
        ubicacion_service.reportar(vid, lat, lon, viaje_id)
        print(f"  GPS #{i + 1}: ({lat}, {lon})")
        time.sleep(1)
    print("  Verificar en Cassandra (ubicaciones_por_vehiculo) y Redis (vehiculo:{id}:pos).")

    _narrar("Paso 7: Finalizar el viaje (toca 4 bases en simultaneo)")
    viaje_service.finalizar(viaje_id, distancia_km=8.5, duracion_min=22)
    print("  Mongo:     viaje.estado = FINALIZADO")
    print("  Cassandra: ultima_actividad_conductor + viajes_finalizados_por_dia")
    print("  Neo4j:     arista (:Usuario)-[:VIAJO_CON {cantidad_viajes: 1}]->(:Conductor)")
    print("  Redis:     cache:viajes_promedio invalidado")

    _narrar("Paso 8: Procesar pago con TARJETA por $2500")
    pago_service.procesar(viaje_id, 2500, 500, 1250, 750, 0, "TARJETA")
    print("  Verificar en Mongo (coleccion pagos).")

    _narrar("Paso 9: El usuario deja una resena con rating 5 (toca 4 bases)")
    resena_service.crear(
        viaje_id, "U_A_C", uid, f"Diego {suf}", cid, f"Ana {suf}",
        rating=5, comentario="Excelente viaje",
    )
    print("  Mongo:     coleccion resenas")
    print("  Postgres:  conductor.rating_promedio recalculado")
    print("  Neo4j:     nodo Conductor con rating actualizado")
    print("  Redis:     cache:top3_resenadores invalidado")

    _narrar("Paso 10: Logout — borra sesion en Redis y audita en Mongo")
    auth_service.logout(token)
    print("  Verificar en Redis (clave session ya no existe).")

    _narrar("Ahora ejecuto los 7 casos de uso del enunciado:")

    print("\nCaso 1 — Top 3 resenadores (Mongo aggregate + cache Redis):")
    for item in caso_01_top_resenadores.ejecutar():
        print(f"  {item['nombre']:30s} {item['cantidad']:>5} resenas")

    print("\nCaso 2 — Metodo de pago menos usado (Mongo):")
    print(f"  -> {caso_02_metodo_pago.ejecutar()}")

    print("\nCaso 3 — Conductores inactivos ultimo mes (Cassandra + Postgres):")
    for c in caso_03_conductores_inactivos.ejecutar():
        print(f"  {c['nombre']:30s} ({c['email']})")

    print("\nCaso 4 — Tiempo promedio de viajes (Cassandra + cache Redis):")
    print(f"  -> {caso_04_promedio_viajes.ejecutar():.2f} min")

    print("\nCaso 5 — Coincidencias pasajero-conductor en >1 viaje (Neo4j):")
    for c in caso_05_coincidencias.ejecutar():
        print(f"  {c['pasajero']:20s} <-> {c['conductor']:20s} ({c['viajes']} viajes)")

    print("\nCaso 6 — Toyota con patente terminada en D (Neo4j):")
    print(f"  -> {caso_06_toyota_patente_d.ejecutar()} vehiculos")

    print("\nCaso 7 — Resenas con rating 5 o <2 (Mongo):")
    for r in caso_07_resenas_extremas.ejecutar()[:5]:
        print(f"  rating {r['rating']} - {r['autor']['nombre']:20s} -> {r['destinatario']['nombre']:20s}")

    print("\n" + "=" * 60)
    print("  FIN DE LA DEMO AUTOMATICA")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
