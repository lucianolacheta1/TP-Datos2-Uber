"""Excepciones del dominio del TP Uber."""


class DomainError(Exception):
    """Error base del dominio. Capturable por las capas superiores."""


class EntidadInexistente(DomainError):
    """Una entidad referenciada no existe."""


class UsuarioInexistente(EntidadInexistente):
    pass


class ConductorInexistente(EntidadInexistente):
    pass


class VehiculoInexistente(EntidadInexistente):
    pass


class ViajeNoEncontrado(EntidadInexistente):
    pass


class CredencialesInvalidas(DomainError):
    """Email o password incorrectos."""


class SesionExpirada(DomainError):
    """La sesion Redis vencio o no existe."""


class EstadoInvalido(DomainError):
    """Se intento una transicion de estado no permitida (ej. finalizar un viaje PENDIENTE)."""
