"""Excepciones propias del dominio de Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Excepción base para los errores controlados de la aplicación."""


class DatosInvalidosError(ErrorSoftwareFJ):
    """Se genera cuando un dato no cumple el formato o rango esperado."""


class ClienteInvalidoError(DatosInvalidosError):
    """Datos personales de un cliente inválidos."""


class ClienteDuplicadoError(ErrorSoftwareFJ):
    """La identificación del cliente ya se encuentra registrada."""


class ClienteNoEncontradoError(ErrorSoftwareFJ):
    """No existe un cliente con la identificación solicitada."""


class ServicioInvalidoError(DatosInvalidosError):
    """Configuración incorrecta de un servicio."""


class ServicioDuplicadoError(ErrorSoftwareFJ):
    """El código del servicio ya se encuentra registrado."""


class ServicioNoEncontradoError(ErrorSoftwareFJ):
    """No existe un servicio con el código solicitado."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio o recurso no está disponible para el intervalo solicitado."""


class ReservaInvalidaError(DatosInvalidosError):
    """Una reserva contiene datos o parámetros inválidos."""


class ReservaDuplicadaError(ErrorSoftwareFJ):
    """El código de la reserva ya se encuentra registrado."""


class ReservaNoEncontradaError(ErrorSoftwareFJ):
    """No existe una reserva con el código solicitado."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """La operación no está permitida para el estado actual del objeto."""


class ErrorCalculoError(ErrorSoftwareFJ):
    """Se produjo un error al calcular el costo de un servicio o reserva."""


class ErrorRegistroError(ErrorSoftwareFJ):
    """No fue posible registrar un evento o error en el archivo de logs."""
