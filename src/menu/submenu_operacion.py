"""Submenu de operaciones de negocio. Requiere sesión activa.

El menú se adapta al rol (USUARIO o CONDUCTOR) y nunca pide IDs internos:
todas las entidades se eligen de listas numeradas obtenidas via services.
"""
import random
from src.services import (
    auth_service, vehiculo_service, viaje_service, pago_service,
    resena_service, ubicacion_service,
)
from src.utils.errors import DomainError
from src.menu import formato

METODOS_PAGO = ("TARJETA", "EFECTIVO", "BILLETERA_VIRTUAL")


def loop(sesion: dict) -> None:
    if not _refrescar_sesion(sesion):
        return

    while True:
        # La sesión puede expirar mientras se navega (TTL en Redis)
        if not _refrescar_sesion(sesion):
            return
        tipo = sesion["data"]["tipo"]
        formato.subtitulo(f"Operación — {sesion['data']['nombre']} ({tipo})")

        if tipo == "CONDUCTOR":
            print("1. Registrar vehículo")
            print("2. Iniciar viaje asignado")
            print("3. Finalizar viaje en curso")
            print("4. Reportar GPS de mi vehículo")
            print("5. Crear reseña de un viaje")
            print("6. Volver")
            op = input("\nElegí una opción: ").strip()
            if op == "1":
                _registrar_vehiculo(sesion)
            elif op == "2":
                _iniciar_viaje(sesion)
            elif op == "3":
                _finalizar_viaje(sesion)
            elif op == "4":
                _reportar_gps(sesion)
            elif op == "5":
                _crear_resena(sesion)
            elif op == "6":
                return
            else:
                formato.error("Opción inválida.")
        else:  # USUARIO
            print("1. Solicitar viaje")
            print("2. Pagar un viaje finalizado")
            print("3. Crear reseña de un viaje")
            print("4. Volver")
            op = input("\nElegí una opción: ").strip()
            if op == "1":
                _solicitar_viaje(sesion)
            elif op == "2":
                _procesar_pago(sesion)
            elif op == "3":
                _crear_resena(sesion)
            elif op == "4":
                return
            else:
                formato.error("Opción inválida.")


def _refrescar_sesion(sesion: dict) -> bool:
    """Re-valida el token contra Redis. Si expiró, limpia la sesión local."""
    token = sesion.get("token")
    if not token:
        formato.error("Necesitás iniciar sesión primero.")
        formato.pausa()
        return False
    data = auth_service.validate_session(token)
    if data is None:
        sesion["token"] = None
        sesion["data"] = None
        formato.error("Tu sesión expiró. Iniciá sesión de nuevo.")
        formato.pausa()
        return False
    sesion["data"] = data
    return True


# ---------------- helpers de etiquetas ----------------

def _etiqueta_viaje(v: dict) -> str:
    origen = (v.get("origen") or {}).get("direccion", "?")
    destino = (v.get("destino") or {}).get("direccion", "?")
    pasajero = (v.get("usuario_snapshot") or {}).get("nombre", "?")
    conductor = (v.get("conductor_snapshot") or {}).get("nombre", "?")
    ts = v.get("ts_solicitud")
    fecha = ts.strftime("%d/%m %H:%M") if ts else "?"
    return f"{origen} -> {destino} | pasajero: {pasajero} | conductor: {conductor} | {fecha}"


def _etiqueta_vehiculo(v: dict) -> str:
    anio = f" {v['anio']}" if v.get("anio") else ""
    return f"{v['marca']} {v['modelo']}{anio} — patente {v['placa']}"


# ---------------- CONDUCTOR ----------------

def _registrar_vehiculo(sesion: dict) -> None:
    cid = sesion["data"]["user_id"]
    placa = formato.pedir_input("Placa")
    marca = formato.pedir_input("Marca")
    modelo = formato.pedir_input("Modelo")
    anio = formato.pedir_input("Año (opcional)", default="")
    color = formato.pedir_input("Color (opcional)", default="")
    tipo = formato.pedir_input("Tipo (sedan/SUV/moto/...) (opcional)", default="")
    if anio and not anio.isdigit():
        formato.error("El año debe ser un número.")
        formato.pausa()
        return
    try:
        vid = vehiculo_service.registrar(
            cid, placa, marca, modelo,
            anio=int(anio) if anio else None,
            color=color or None,
            tipo=tipo or None,
        )
        formato.exito(f"Vehículo {placa} registrado.")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"No se pudo registrar: {e}")
    formato.pausa()


def _iniciar_viaje(sesion: dict) -> None:
    cid = sesion["data"]["user_id"]
    pendientes = viaje_service.listar_de_conductor(cid, "PENDIENTE")
    if not pendientes:
        formato.info("No tenés viajes pendientes para iniciar.")
        formato.pausa()
        return
    print("\nTus viajes pendientes:")
    viaje = formato.elegir_de_lista(pendientes, _etiqueta_viaje)
    if viaje is None:
        return
    try:
        if viaje_service.iniciar(viaje["_id"]):
            formato.exito("Viaje iniciado (EN_CURSO).")
        else:
            formato.error("No se pudo iniciar (¿cambió de estado?).")
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _finalizar_viaje(sesion: dict) -> None:
    cid = sesion["data"]["user_id"]
    en_curso = viaje_service.listar_de_conductor(cid, "EN_CURSO")
    if not en_curso:
        formato.info("No tenés viajes en curso para finalizar.")
        formato.pausa()
        return
    print("\nTus viajes en curso:")
    viaje = formato.elegir_de_lista(en_curso, _etiqueta_viaje)
    if viaje is None:
        return
    distancia = formato.pedir_decimal("Distancia (km)", minimo=0.1)
    duracion = formato.pedir_entero("Duración (min)", minimo=1)
    try:
        viaje_service.finalizar(viaje["_id"], distancia, duracion)
        formato.exito("Viaje finalizado. Proyectado a Cassandra, Neo4j y Redis.")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _reportar_gps(sesion: dict) -> None:
    cid = sesion["data"]["user_id"]
    vehiculos = vehiculo_service.listar_de_conductor(cid)
    if not vehiculos:
        formato.info("No tenés vehículos registrados. Registrá uno primero.")
        formato.pausa()
        return
    print("\nTus vehículos:")
    vehiculo = formato.elegir_de_lista(vehiculos, _etiqueta_vehiculo)
    if vehiculo is None:
        return
    try:
        # Para la demo: lat/lon aleatorios cerca de CABA
        lat = -34.6 + random.uniform(-0.1, 0.1)
        lon = -58.4 + random.uniform(-0.1, 0.1)
        ubicacion_service.reportar(vehiculo["id"], lat, lon)
        formato.exito(f"GPS reportado para {vehiculo['placa']}: ({lat:.4f}, {lon:.4f})")
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


# ---------------- USUARIO ----------------

def _solicitar_viaje(sesion: dict) -> None:
    uid = sesion["data"]["user_id"]
    disponibles = vehiculo_service.listar_conductores_disponibles()
    if not disponibles:
        formato.info("No hay conductores con vehículo disponibles en este momento.")
        formato.pausa()
        return

    print("\nConductores disponibles:")
    elegido = formato.elegir_de_lista(
        disponibles,
        lambda d: f"{d['conductor']['nombre']} (rating {d['conductor']['rating_promedio']:.1f}) "
                  f"— {len(d['vehiculos'])} vehículo/s",
    )
    if elegido is None:
        return

    vehiculos = elegido["vehiculos"]
    if len(vehiculos) == 1:
        vehiculo = vehiculos[0]
        formato.info(f"Vehículo: {_etiqueta_vehiculo(vehiculo)}")
    else:
        print("\nVehículos del conductor:")
        vehiculo = formato.elegir_de_lista(vehiculos, _etiqueta_vehiculo)
        if vehiculo is None:
            return

    origen = formato.pedir_input("Origen (dirección)")
    destino = formato.pedir_input("Destino (dirección)")
    try:
        viaje_service.solicitar(
            uid, elegido["conductor"]["id"], vehiculo["id"],
            origen={"lat": -34.6, "lon": -58.4, "direccion": origen},
            destino={"lat": -34.55, "lon": -58.45, "direccion": destino},
        )
        formato.exito(
            f"Viaje solicitado a {elegido['conductor']['nombre']} (estado PENDIENTE). "
            "El conductor debe iniciarlo."
        )
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _procesar_pago(sesion: dict) -> None:
    uid = sesion["data"]["user_id"]
    finalizados = viaje_service.listar_de_usuario(uid, "FINALIZADO")
    if not finalizados:
        formato.info("No tenés viajes finalizados para pagar.")
        formato.pausa()
        return
    print("\nTus viajes finalizados:")
    viaje = formato.elegir_de_lista(finalizados, _etiqueta_viaje)
    if viaje is None:
        return
    monto = formato.pedir_decimal("Monto total", minimo=0.01)
    print("Métodos de pago: " + " / ".join(METODOS_PAGO))
    metodo = formato.pedir_input("Método", default="TARJETA").strip().upper()
    if metodo not in METODOS_PAGO:
        formato.error(f"Método inválido. Opciones: {', '.join(METODOS_PAGO)}")
        formato.pausa()
        return
    try:
        pago_service.procesar(
            viaje["_id"], monto, tarifa_base=500,
            tarifa_distancia=monto * 0.5, tarifa_tiempo=monto * 0.3,
            cargos_extra=0, metodo_pago=metodo,
        )
        formato.exito(f"Pago de ${monto:.2f} procesado con {metodo}.")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


# ---------------- ambos roles ----------------

def _crear_resena(sesion: dict) -> None:
    """El destinatario se deriva del viaje elegido: nunca se piden IDs."""
    data = sesion["data"]
    es_usuario = data["tipo"] == "USUARIO"
    if es_usuario:
        finalizados = viaje_service.listar_de_usuario(data["user_id"], "FINALIZADO")
    else:
        finalizados = viaje_service.listar_de_conductor(data["user_id"], "FINALIZADO")
    if not finalizados:
        formato.info("No tenés viajes finalizados para reseñar.")
        formato.pausa()
        return

    print("\nTus viajes finalizados:")
    viaje = formato.elegir_de_lista(finalizados, _etiqueta_viaje)
    if viaje is None:
        return

    # El destinatario es "el otro" participante del viaje
    if es_usuario:
        tipo = "U_A_C"
        destinatario_id = viaje["conductor_id"]
        destinatario_nombre = (viaje.get("conductor_snapshot") or {}).get("nombre", "?")
    else:
        tipo = "C_A_U"
        destinatario_id = viaje["usuario_id"]
        destinatario_nombre = (viaje.get("usuario_snapshot") or {}).get("nombre", "?")

    formato.info(f"Vas a reseñar a: {destinatario_nombre}")
    rating = formato.pedir_entero("Rating (1-5)", minimo=1, maximo=5)
    comentario = formato.pedir_input("Comentario (opcional)", default="")
    try:
        resena_service.crear(
            viaje["_id"], tipo, data["user_id"], data["nombre"],
            destinatario_id, destinatario_nombre,
            rating, comentario,
        )
        formato.exito(f"Reseña de {rating} estrellas para {destinatario_nombre} creada.")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()
