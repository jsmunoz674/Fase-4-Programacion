"""Entidad Reserva y su ciclo de vida: pendiente, confirmada, cancelada y finalizada."""
from datetime import datetime
from decimal import Decimal

from excepciones.errores import ReservaInvalidaError, OperacionNoPermitidaError
from modelos.cliente import Cliente
from modelos.entidad import EntidadSistema
from modelos.servicio import Servicio


class Reserva(EntidadSistema):
    """Relaciona un cliente y un servicio para una fecha, duración y parámetros."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"

    def __init__(self, identificador, cliente, servicio, fecha_inicio,
                 duracion, parametros=None):
        super().__init__(identificador)
        self._cliente = cliente
        self._servicio = servicio
        self._fecha_inicio = fecha_inicio
        self._duracion = duracion
        self._parametros = parametros
        self._estado = self.PENDIENTE
        self._costo_final = None
        self.validar_datos()

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def fecha_inicio(self):
        return self._fecha_inicio

    @property
    def fecha_fin(self):
        return self._fecha_fin

    @property
    def duracion(self):
        return self._duracion

    @property
    def parametros(self):
        return dict(self._parametros)

    @property
    def estado(self):
        return self._estado

    @property
    def costo_final(self):
        return self._costo_final

    def validar_datos(self):
        if not isinstance(self.cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")
        if not isinstance(self.servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")
        if not isinstance(self.fecha_inicio, datetime):
            raise ReservaInvalidaError("La fecha de inicio debe ser un datetime.")
        self._duracion = self.servicio._validar_duracion(self._duracion)
        self._parametros = self.servicio.validar_parametros(
            self._duracion, self._parametros
        )
        self._fecha_fin = self.servicio.calcular_fecha_fin(
            self._fecha_inicio, self._duracion
        )

    def confirmar(self, reservas):
        if self.estado != self.PENDIENTE:
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )
        self.servicio.verificar_disponibilidad(
            self.fecha_inicio, self.fecha_fin, reservas,
            self.parametros, reserva_excluir=self
        )
        self._estado = self.CONFIRMADA
        return self

    def cancelar(self):
        if self.estado not in (self.PENDIENTE, self.CONFIRMADA):
            raise OperacionNoPermitidaError(
                "Solo se pueden cancelar reservas pendientes o confirmadas."
            )
        self._estado = self.CANCELADA
        return self

    def procesar(self, impuesto=0, descuento=0):
        if self.estado != self.CONFIRMADA:
            raise OperacionNoPermitidaError(
                "Solo se pueden procesar reservas confirmadas."
            )
        total = self.servicio.calcular_costo(
            self.duracion, impuesto=impuesto, descuento=descuento,
            **self.parametros
        )
        self._costo_final = Decimal(total)
        self._estado = self.FINALIZADA
        return self._costo_final

    def describir(self):
        unidad = self.servicio.UNIDAD_DURACION
        texto = (
            f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} "
            f"| Servicio: {self.servicio.nombre} | "
            f"{self.fecha_inicio:%Y-%m-%d %H:%M} a "
            f"{self.fecha_fin:%Y-%m-%d %H:%M} "
            f"| Duración: {self.duracion} {unidad} | Estado: {self.estado}"
        )
        if self.costo_final is not None:
            texto += f" | Total: ${self.costo_final:,.2f} COP"
        return texto

    def __str__(self):
        return self.describir()
