"""Menu principal — orquesta los 4 submenus."""
from src.menu import (
    submenu_cuentas,
    submenu_operacion,
    submenu_consultas,
    submenu_admin,
    formato,
)

# Sesion actual del usuario, mutable y compartida con los submenus
_sesion = {"token": None, "data": None}


def loop() -> None:
    """Loop infinito del menu principal hasta que el usuario salga."""
    formato.titulo("TP UBER — Datos 2 (UADE)")

    while True:
        _imprimir_estado_sesion()
        print("\n1. Cuentas")
        print("2. Operación")
        print("3. Consultas (7 casos de uso)")
        print("4. Administración")
        print("5. Salir")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            submenu_cuentas.loop(_sesion)
        elif op == "2":
            submenu_operacion.loop(_sesion)
        elif op == "3":
            submenu_consultas.loop()
        elif op == "4":
            submenu_admin.loop()
        elif op == "5":
            formato.info("Hasta luego.")
            return
        else:
            formato.error("Opción inválida.")


def _imprimir_estado_sesion() -> None:
    if _sesion.get("data"):
        formato.info(f"Sesión activa: {_sesion['data']['nombre']} ({_sesion['data']['tipo']})")
    else:
        formato.info("Sin sesión activa")
