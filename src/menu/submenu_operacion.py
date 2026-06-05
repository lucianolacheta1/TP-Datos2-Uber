"""Submenu de operaciones de negocio. Requiere sesión activa."""
import random
from src.services import (
    vehiculo_service, viaje_service, pago_service,
    resena_service, ubicacion_service,
)
from src.utils.errors import DomainError
from src.menu import formato


def loop(sesion: dict) -> None:
    if not sesion.get("data"):
        formato.error("Necesitás iniciar sesión primero.")
        formato.pausa()
        return

    while True:
        formato.subtitulo(f"Operación — {sesion['data']['nombre']} ({sesion['data']['tipo']})")
        print("1. Registrar vehículo (solo CONDUCTOR)")
        print("2. Solicitar viaje (solo USUARIO)")
        print("3. Iniciar viaje (solo CONDUCTOR)")
        print("4. Finalizar viaje (solo CONDUCTOR)")
        print("5. Reportar GPS de un vehículo")
        print("6. Procesar pago de un viaje")
        print("7. Crear reseña")
        print("8. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _registrar_vehiculo(sesion)
        elif op == "2":
            _solicitar_viaje(sesion)
        elif op == "3":
            _iniciar_viaje()
        elif op == "4":
            _finalizar_viaje()
        elif op == "5":
            _reportar_gps()
        elif op == "6":
            _procesar_pago(sesion)
        elif op == "7":
            _crear_resena(sesion)
        elif op == "8":
            return
        else:
            formato.error("Opción inválida.")


def _registrar_vehiculo(sesion: dict) -> None:
    if sesion["data"]["tipo"] != "CONDUCTOR":
        formato.error("Solo los CONDUCTORES pueden registrar vehículos.")
        formato.pausa()
        return
    cid = sesion["data"]["user_id"]
    placa = formato.pedir_input("Placa")
    marca = formato.pedir_input("Marca")
    modelo = formato.pedir_input("Modelo")
    anio = formato.pedir_input("Año (opcional)", default="")
    color = formato.pedir_input("Color (opcional)", default="")
    tipo = formato.pedir_input("Tipo (sedan/SUV/moto/...) (opcional)", default="")
    try:
        vid = vehiculo_service.registrar(
            cid, placa, marca, modelo,
            anio=int(anio) if anio else None,
            color=color or None,
            tipo=tipo or None,
        )
        formato.exito(f"Vehículo registrado con id {vid}")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"No se pudo registrar: {e}")
    formato.pausa()


def _solicitar_viaje(sesion: dict) -> None:
    if sesion["data"]["tipo"] != "USUARIO":
        formato.error("Solo los USUARIOS pueden solicitar viajes.")
        formato.pausa()
        return
    uid = sesion["data"]["user_id"]
    cid = formato.pedir_input("ID del conductor")
    vid = formato.pedir_input("ID del vehículo")
    origen = formato.pedir_input("Origen (descripción)")
    destino = formato.pedir_input("Destino (descripción)")
    try:
        viaje_id = viaje_service.solicitar(
            uid, cid, vid,
            origen={"lat": -34.6, "lon": -58.4, "direccion": origen},
            destino={"lat": -34.55, "lon": -58.45, "direccion": destino},
        )
        formato.exito(f"Viaje solicitado con id {viaje_id} (estado PENDIENTE)")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _iniciar_viaje() -> None:
    viaje_id = formato.pedir_input("ID del viaje a iniciar")
    try:
        ok = viaje_service.iniciar(viaje_id)
        if ok:
            formato.exito("Viaje iniciado (EN_CURSO).")
        else:
            formato.error("No se pudo iniciar (¿no estaba PENDIENTE?).")
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _finalizar_viaje() -> None:
    viaje_id = formato.pedir_input("ID del viaje a finalizar")
    try:
        distancia = float(formato.pedir_input("Distancia (km)"))
        duracion = int(formato.pedir_input("Duración (min)"))
        viaje_service.finalizar(viaje_id, distancia, duracion)
        formato.exito("Viaje finalizado.")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _reportar_gps() -> None:
    vid = formato.pedir_input("ID del vehículo")
    try:
        # Para la demo: lat/lon aleatorios cerca de CABA
        lat = -34.6 + random.uniform(-0.1, 0.1)
        lon = -58.4 + random.uniform(-0.1, 0.1)
        ubicacion_service.reportar(vid, lat, lon)
        formato.exito(f"GPS reportado: ({lat:.4f}, {lon:.4f})")
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _procesar_pago(sesion: dict) -> None:
    viaje_id = formato.pedir_input("ID del viaje")
    try:
        monto = float(formato.pedir_input("Monto total"))
        metodo = formato.pedir_input("Método (TARJETA/EFECTIVO/BILLETERA_VIRTUAL)", default="TARJETA")
        pago_id = pago_service.procesar(
            viaje_id, monto, tarifa_base=500,
            tarifa_distancia=monto * 0.5, tarifa_tiempo=monto * 0.3,
            cargos_extra=0, metodo_pago=metodo,
        )
        formato.exito(f"Pago procesado con id {pago_id}")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _crear_resena(sesion: dict) -> None:
    viaje_id = formato.pedir_input("ID del viaje")
    autor_id = sesion["data"]["user_id"]
    autor_nombre = sesion["data"]["nombre"]
    destinatario_id = formato.pedir_input("ID del destinatario (el otro participante)")
    destinatario_nombre = formato.pedir_input("Nombre del destinatario")
    tipo = "U_A_C" if sesion["data"]["tipo"] == "USUARIO" else "C_A_U"
    try:
        rating = int(formato.pedir_input("Rating (1-5)"))
        comentario = formato.pedir_input("Comentario")
        rid = resena_service.crear(
            viaje_id, tipo, autor_id, autor_nombre,
            destinatario_id, destinatario_nombre,
            rating, comentario,
        )
        formato.exito(f"Reseña creada con id {rid}")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()
