"""Gestor central de clientes, servicios y reservas de Software FJ."""
import logging
from functools import wraps

from configuracion import RUTA_LOG
from excepciones.errores import (
    ErrorSoftwareFJ,
    ClienteDuplicadoError,
    ClienteNoEncontradoError,
    ServicioDuplicadoError,
    ServicioNoEncontradoError,
    ReservaDuplicadaError,
    ReservaNoEncontradaError,
)
from modelos.cliente import Cliente
from modelos.servicio import Servicio
from modelos.servicios_especializados import ServicioSala, ServicioEquipo, ServicioAsesoria
from modelos.reserva import Reserva


def configurar_logger():
    """Configura el archivo de eventos y errores sin duplicar manejadores."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    ruta = str(RUTA_LOG)
    if not any(getattr(handler, "baseFilename", None) == ruta for handler in logger.handlers):
        handler = logging.FileHandler(RUTA_LOG, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formato)
        logger.addHandler(handler)
    return logger


def registrar_operacion(metodo):
    """Registra éxitos y errores de los métodos públicos del gestor.

    El except registra el error. El else registra las operaciones exitosas.
    El finally registra el cierre de cada intento. Los errores inesperados se
    transforman en ErrorSoftwareFJ conservando su causa mediante 'raise from'.
    """
    @wraps(metodo)
    def envoltura(self, *args, **kwargs):
        try:
            resultado = metodo(self, *args, **kwargs)
        except Exception as exc:
            self._logger.exception("Error durante %s: %s", metodo.__name__, exc)
            if isinstance(exc, ErrorSoftwareFJ):
                raise
            raise ErrorSoftwareFJ(
                f"Ocurrió un error inesperado durante {metodo.__name__}."
            ) from exc
        else:
            self._logger.info("Operación %s ejecutada correctamente.", metodo.__name__)
            return resultado
        finally:
            self._logger.debug("Finalizó el intento de operación: %s.", metodo.__name__)

    return envoltura


class SistemaSoftwareFJ:
    """Administra los objetos en memoria; no utiliza bases de datos."""

    def __init__(self):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        self._logger = configurar_logger()
        self._logger.info("Sistema Software FJ iniciado.")

    @property
    def clientes(self):
        return tuple(self._clientes)

    @property
    def servicios(self):
        return tuple(self._servicios)

    @property
    def reservas(self):
        return tuple(self._reservas)

    @registrar_operacion
    def registrar_cliente(self, identificacion, nombre, correo, telefono) -> Cliente:
        cliente = Cliente(identificacion, nombre, correo, telefono)
        if any(actual.identificador == cliente.identificador for actual in self._clientes):
            raise ClienteDuplicadoError(
                f"Ya existe un cliente con identificación {cliente.identificador}."
            )
        self._clientes.append(cliente)
        return cliente

    def buscar_cliente(self, identificacion) -> Cliente:
        if not isinstance(identificacion, str):
            raise ClienteNoEncontradoError("La identificación debe ingresarse como texto.")
        codigo = identificacion.strip().upper()
        for cliente in self._clientes:
            if cliente.identificador == codigo:
                return cliente
        raise ClienteNoEncontradoError(f"No se encontró el cliente {codigo}.")

    def _registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise TypeError("El objeto recibido no es un Servicio válido.")
        if any(actual.identificador == servicio.identificador for actual in self._servicios):
            raise ServicioDuplicadoError(
                f"Ya existe un servicio con código {servicio.identificador}."
            )
        self._servicios.append(servicio)
        return servicio

    @registrar_operacion
    def crear_servicio_sala(self, identificador, nombre, tarifa=None, capacidad=12) -> ServicioSala:
        if tarifa is None:
            servicio = ServicioSala(identificador, nombre, capacidad=capacidad)
        else:
            servicio = ServicioSala(identificador, nombre, tarifa=tarifa, capacidad=capacidad)
        return self._registrar_servicio(servicio)

    @registrar_operacion
    def crear_servicio_equipo(
        self, identificador, nombre, tarifa=None, cantidad_disponible=10
    ) -> ServicioEquipo:
        if tarifa is None:
            servicio = ServicioEquipo(
                identificador, nombre, cantidad_disponible=cantidad_disponible
            )
        else:
            servicio = ServicioEquipo(
                identificador, nombre, tarifa=tarifa,
                cantidad_disponible=cantidad_disponible
            )
        return self._registrar_servicio(servicio)

    @registrar_operacion
    def crear_servicio_asesoria(
        self, identificador, nombre, especialista, tarifa=None
    ) -> ServicioAsesoria:
        if tarifa is None:
            servicio = ServicioAsesoria(identificador, nombre, especialista)
        else:
            servicio = ServicioAsesoria(identificador, nombre, especialista, tarifa)
        return self._registrar_servicio(servicio)

    def buscar_servicio(self, identificador) -> Servicio:
        if not isinstance(identificador, str):
            raise ServicioNoEncontradoError("El código del servicio debe ingresarse como texto.")
        codigo = identificador.strip().upper()
        for servicio in self._servicios:
            if servicio.identificador == codigo:
                return servicio
        raise ServicioNoEncontradoError(f"No se encontró el servicio {codigo}.")

    @registrar_operacion
    def crear_reserva(
        self, identificador, identificacion_cliente, codigo_servicio,
        fecha_inicio, duracion, parametros=None
    ) -> Reserva:
        reserva = Reserva(
            identificador,
            self.buscar_cliente(identificacion_cliente),
            self.buscar_servicio(codigo_servicio),
            fecha_inicio,
            duracion,
            parametros,
        )
        if any(actual.identificador == reserva.identificador for actual in self._reservas):
            raise ReservaDuplicadaError(
                f"Ya existe una reserva con código {reserva.identificador}."
            )
        reserva.servicio.verificar_disponibilidad(
            reserva.fecha_inicio,
            reserva.fecha_fin,
            self._reservas,
            reserva.parametros,
        )
        self._reservas.append(reserva)
        return reserva

    def buscar_reserva(self, identificador) -> Reserva:
        if not isinstance(identificador, str):
            raise ReservaNoEncontradaError("El código de reserva debe ingresarse como texto.")
        codigo = identificador.strip().upper()
        for reserva in self._reservas:
            if reserva.identificador == codigo:
                return reserva
        raise ReservaNoEncontradaError(f"No se encontró la reserva {codigo}.")

    @registrar_operacion
    def confirmar_reserva(self, identificador) -> Reserva:
        reserva = self.buscar_reserva(identificador)
        reserva.confirmar(self._reservas)
        return reserva

    @registrar_operacion
    def cancelar_reserva(self, identificador) -> Reserva:
        reserva = self.buscar_reserva(identificador)
        reserva.cancelar()
        return reserva

    @registrar_operacion
    def procesar_reserva(self, identificador, impuesto=0, descuento=0):
        reserva = self.buscar_reserva(identificador)
        return reserva.procesar(impuesto=impuesto, descuento=descuento)

    def listar_clientes(self):
        return [cliente.describir() for cliente in self._clientes]

    def listar_servicios(self):
        return [servicio.describir_servicio() for servicio in self._servicios]

    def listar_reservas(self):
        return [reserva.describir() for reserva in self._reservas]

    def resumen(self) -> dict:
        """Devuelve un resumen calculado únicamente desde las listas en memoria."""
        estados = {estado: 0 for estado in (
            Reserva.PENDIENTE, Reserva.CONFIRMADA,
            Reserva.CANCELADA, Reserva.FINALIZADA
        )}
        total_procesado = 0
        for reserva in self._reservas:
            estados[reserva.estado] += 1
            if reserva.costo_final is not None:
                total_procesado += reserva.costo_final
        return {
            "clientes": len(self._clientes),
            "servicios": len(self._servicios),
            "reservas": len(self._reservas),
            "estados": estados,
            "total_procesado": total_procesado,
        }
