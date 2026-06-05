"""Tests minimalistas del menu: verifican que los modulos importan."""


def test_main_menu_importa():
    from src.menu import main_menu
    assert main_menu.loop is not None


def test_submenu_cuentas_importa():
    from src.menu import submenu_cuentas
    assert submenu_cuentas.loop is not None


def test_submenu_operacion_importa():
    from src.menu import submenu_operacion
    assert submenu_operacion.loop is not None


def test_submenu_consultas_importa():
    from src.menu import submenu_consultas
    assert submenu_consultas.loop is not None


def test_submenu_admin_importa():
    from src.menu import submenu_admin
    assert submenu_admin.loop is not None


def test_formato_helpers_existen():
    from src.menu import formato
    assert formato.titulo is not None
    assert formato.error is not None
    assert formato.exito is not None
    assert formato.tabla is not None
    assert formato.confirmar is not None
