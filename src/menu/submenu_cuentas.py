"""Submenu de gestion de cuentas: registro, login, logout."""
import getpass

from src.services import auth_service
from src.utils.errors import CredencialesInvalidas
from src.menu import formato


def loop(sesion: dict) -> None:
    """Loop del submenu. sesion es un dict mutable con token/data actuales."""
    while True:
        formato.subtitulo("Cuentas")
        _imprimir_estado_sesion(sesion)
        print("1. Registrar como usuario (pasajero)")
        print("2. Registrar como conductor")
        print("3. Iniciar sesión")
        print("4. Cerrar sesión")
        print("5. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _registrar_usuario()
        elif op == "2":
            _registrar_conductor()
        elif op == "3":
            _login(sesion)
        elif op == "4":
            _logout(sesion)
        elif op == "5":
            return
        else:
            formato.error("Opción inválida.")


def _imprimir_estado_sesion(sesion: dict) -> None:
    if sesion.get("data"):
        formato.info(f"Sesión activa: {sesion['data']['nombre']} ({sesion['data']['tipo']})")
    else:
        formato.info("Sin sesión")


def _registrar_usuario() -> None:
    email = formato.pedir_input("Email").lower()
    password = getpass.getpass("Password: ")
    nombre = formato.pedir_input("Nombre completo")
    telefono = formato.pedir_input("Teléfono (opcional)", default="")
    try:
        uid = auth_service.register_usuario(email, password, nombre, telefono or None)
        formato.exito(f"Usuario registrado con id {uid}")
    except Exception as e:
        formato.error(f"No se pudo registrar: {e}")
    formato.pausa()


def _registrar_conductor() -> None:
    email = formato.pedir_input("Email").lower()
    password = getpass.getpass("Password: ")
    nombre = formato.pedir_input("Nombre completo")
    licencia = formato.pedir_input("Nro. de licencia")
    telefono = formato.pedir_input("Teléfono (opcional)", default="")
    try:
        cid = auth_service.register_conductor(email, password, nombre, licencia, telefono or None)
        formato.exito(f"Conductor registrado con id {cid}")
    except Exception as e:
        formato.error(f"No se pudo registrar: {e}")
    formato.pausa()


def _login(sesion: dict) -> None:
    if sesion.get("data"):
        formato.error("Ya hay una sesión activa. Cerrá sesión primero.")
        formato.pausa()
        return
    email = formato.pedir_input("Email").lower()
    password = getpass.getpass("Password: ")
    tipo = formato.pedir_input("Tipo de cuenta (USUARIO/CONDUCTOR)", default="USUARIO").upper()
    if tipo not in ("USUARIO", "CONDUCTOR"):
        formato.error("Tipo de cuenta inválido.")
        formato.pausa()
        return
    try:
        token = auth_service.login(email, password, tipo)
        data = auth_service.validate_session(token)
        sesion["token"] = token
        sesion["data"] = data
        formato.exito(f"Sesión iniciada como {data['nombre']} ({data['tipo']})")
    except CredencialesInvalidas:
        formato.error("Email o password incorrectos.")
    except Exception as e:
        formato.error(f"Error al iniciar sesión: {e}")
    formato.pausa()


def _logout(sesion: dict) -> None:
    if not sesion.get("token"):
        formato.error("No hay sesión activa.")
        formato.pausa()
        return
    auth_service.logout(sesion["token"])
    sesion["token"] = None
    sesion["data"] = None
    formato.exito("Sesión cerrada.")
    formato.pausa()
