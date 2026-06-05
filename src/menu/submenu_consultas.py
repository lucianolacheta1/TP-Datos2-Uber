"""Submenu de consultas: los 7 casos de uso del enunciado."""
from src.casos_uso import (
    caso_01_top_resenadores,
    caso_02_metodo_pago,
    caso_03_conductores_inactivos,
    caso_04_promedio_viajes,
    caso_05_coincidencias,
    caso_06_toyota_patente_d,
    caso_07_resenas_extremas,
)
from src.menu import formato


def loop() -> None:
    while True:
        formato.subtitulo("Consultas — los 7 casos de uso")
        print("1. Top 3 reseñadores")
        print("2. Método de pago menos usado")
        print("3. Conductores inactivos último mes")
        print("4. Tiempo promedio de viajes")
        print("5. Pasajero-conductor con >1 viaje")
        print("6. Toyota con patente terminada en 'D'")
        print("7. Reseñas con rating 5 o <2")
        print("8. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _ejecutar_caso_1()
        elif op == "2":
            _ejecutar_caso_2()
        elif op == "3":
            _ejecutar_caso_3()
        elif op == "4":
            _ejecutar_caso_4()
        elif op == "5":
            _ejecutar_caso_5()
        elif op == "6":
            _ejecutar_caso_6()
        elif op == "7":
            _ejecutar_caso_7()
        elif op == "8":
            return
        else:
            formato.error("Opción inválida.")


def _ejecutar_caso_1() -> None:
    formato.info("Consultando Mongo (con cache Redis)...")
    top = caso_01_top_resenadores.ejecutar()
    if not top:
        formato.info("Sin reseñas aún.")
    else:
        formato.tabla(top, columnas=["nombre", "autor_id", "cantidad"])
    formato.pausa()


def _ejecutar_caso_2() -> None:
    formato.info("Consultando Mongo...")
    metodo = caso_02_metodo_pago.ejecutar()
    if metodo is None:
        formato.info("Sin pagos en la plataforma todavía.")
    else:
        formato.exito(f"Método menos usado: {metodo}")
    formato.pausa()


def _ejecutar_caso_3() -> None:
    formato.info("Consultando Cassandra + Postgres...")
    inactivos = caso_03_conductores_inactivos.ejecutar()
    if not inactivos:
        formato.info("Todos los conductores activos tuvieron viajes en el último mes.")
    else:
        formato.tabla(inactivos, columnas=["nombre", "email", "rating_promedio"])
    formato.pausa()


def _ejecutar_caso_4() -> None:
    formato.info("Consultando Cassandra (con cache Redis)...")
    promedio = caso_04_promedio_viajes.ejecutar()
    formato.exito(f"Tiempo promedio de viaje: {promedio:.2f} min")
    formato.pausa()


def _ejecutar_caso_5() -> None:
    formato.info("Consultando Neo4j...")
    coincidencias = caso_05_coincidencias.ejecutar()
    if not coincidencias:
        formato.info("Nadie coincidió en más de 1 viaje aún.")
    else:
        formato.tabla(coincidencias, columnas=["pasajero", "conductor", "viajes"])
    formato.pausa()


def _ejecutar_caso_6() -> None:
    marca = formato.pedir_input("Marca", default="Toyota")
    sufijo = formato.pedir_input("Patente termina en", default="D")
    formato.info("Consultando Neo4j...")
    cantidad = caso_06_toyota_patente_d.ejecutar(marca, sufijo)
    formato.exito(f"Hay {cantidad} vehículos {marca} con patente terminada en '{sufijo}'.")
    formato.pausa()


def _ejecutar_caso_7() -> None:
    formato.info("Consultando Mongo...")
    extremas = caso_07_resenas_extremas.ejecutar()
    if not extremas:
        formato.info("Sin reseñas extremas todavía.")
    else:
        # Aplanar autor/destinatario para mostrarlo en tabla
        for r in extremas:
            r["autor_nombre"] = r["autor"]["nombre"]
            r["destinatario_nombre"] = r["destinatario"]["nombre"]
        formato.tabla(extremas, columnas=["rating", "autor_nombre", "destinatario_nombre", "comentario"])
    formato.pausa()
