"""Caso de uso 2: método de pago menos utilizado en la plataforma.

Base: Mongo (agregación sobre pagos).
"""
from src.repositories import pago_repo


def ejecutar() -> str | None:
    """Devuelve el nombre del método de pago menos usado, o None si no hay pagos."""
    return pago_repo.metodo_menos_usado()
