"""Implementaciones concretas de los servicios de Software FJ."""
from decimal import Decimal

from configuracion import (
    TARIFA_SALA_POR_HORA,
    TARIFA_EQUIPO_POR_DIA,
    TARIFA_ASESORIA_POR_HORA,
)
from modelos.servicio import Servicio
from excepciones.errores import ServicioInvalidoError, ServicioNoDisponibleError


ESTADOS_QUE_OCUPAN_RECURSO = {"PENDIENTE", "CONFIRMADA"}


def _hay_cruce(inicio_a, fin_a, inicio_b, fin_b) -> bool:
    """Retorna True si dos intervalos de tiempo se superponen."""
    return inicio_a < fin_b and inicio_b < fin_a


class ServicioSala(Servicio):
    """Reserva de una sala identificada individualmente."""

    UNIDAD_DURACION = "horas"

    def __init__(self, identificador, nombre, tarifa=TARIFA_SALA_POR_HORA, capacidad=12):
        self._capacidad = capacidad
        super().__init__(identificador, nombre, tarifa)
        self.validar_datos()

    @property
    def capacidad(self):
        return self._capacidad

    def validar_datos(self):
        super().validar_datos()
        if isinstance(self._capacidad, bool) or not isinstance(self._capacidad, int) or self._capacidad < 1:
            raise ServicioInvalidoError("La capacidad de la sala debe ser un entero positivo.")

    def validar_parametros(self, duracion, parametros=None):
        self._validar_duracion(duracion)
        datos = dict(parametros or {})
        personas = datos.get("personas", 1)
        if isinstance(personas, bool) or not isinstance(personas, int):
            raise ServicioInvalidoError("La cantidad de personas debe ser un número entero.")
        if not 1 <= personas <= self.capacidad:
            raise ServicioInvalidoError(
                f"La sala admite entre 1 y {self.capacidad} personas."
            )
        datos["personas"] = personas
        return datos

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **parametros):
        self.validar_parametros(duracion, parametros)
        base = self.tarifa * self._validar_duracion(duracion)
        return self._aplicar_impuestos_descuentos(base, impuesto, descuento)

    def verificar_disponibilidad(self, fecha_inicio, fecha_fin, reservas, parametros=None, reserva_excluir=None):
        if not self.activo:
            raise ServicioNoDisponibleError(f"El servicio {self.identificador} está inactivo.")
        for reserva in reservas:
            if reserva is reserva_excluir:
                continue
            if reserva.servicio.identificador != self.identificador:
                continue
            if reserva.estado not in ESTADOS_QUE_OCUPAN_RECURSO:
                continue
            if _hay_cruce(fecha_inicio, fecha_fin, reserva.fecha_inicio, reserva.fecha_fin):
                raise ServicioNoDisponibleError(
                    f"La sala {self.identificador} ya tiene una reserva en ese horario."
                )

    def describir_servicio(self):
        return (
            f"Sala | Código: {self.identificador} | {self.nombre} | "
            f"Tarifa: ${self.tarifa:,.0f}/hora COP | Capacidad: {self.capacidad}"
        )


class ServicioEquipo(Servicio):
    """Alquiler de equipos con control de inventario por períodos."""

    UNIDAD_DURACION = "dias"

    def __init__(self, identificador, nombre, tarifa=TARIFA_EQUIPO_POR_DIA, cantidad_disponible=10):
        self._cantidad_disponible = cantidad_disponible
        super().__init__(identificador, nombre, tarifa)
        self.validar_datos()

    @property
    def cantidad_disponible(self):
        return self._cantidad_disponible

    def validar_datos(self):
        super().validar_datos()
        if (
            isinstance(self._cantidad_disponible, bool)
            or not isinstance(self._cantidad_disponible, int)
            or self._cantidad_disponible < 1
        ):
            raise ServicioInvalidoError("La cantidad disponible debe ser un entero positivo.")

    def validar_parametros(self, duracion, parametros=None):
        self._validar_duracion(duracion)
        datos = dict(parametros or {})
        cantidad = datos.get("cantidad", 1)
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise ServicioInvalidoError("La cantidad de equipos debe ser un número entero.")
        if not 1 <= cantidad <= self.cantidad_disponible:
            raise ServicioInvalidoError(
                f"La cantidad solicitada debe estar entre 1 y {self.cantidad_disponible}."
            )
        datos["cantidad"] = cantidad
        return datos

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **parametros):
        datos = self.validar_parametros(duracion, parametros)
        base = self.tarifa * self._validar_duracion(duracion) * Decimal(datos["cantidad"])
        return self._aplicar_impuestos_descuentos(base, impuesto, descuento)

    def verificar_disponibilidad(self, fecha_inicio, fecha_fin, reservas, parametros=None, reserva_excluir=None):
        if not self.activo:
            raise ServicioNoDisponibleError(f"El servicio {self.identificador} está inactivo.")
        datos = self.validar_parametros(1, parametros)
        solicitados = datos["cantidad"]
        ocupados = 0
        for reserva in reservas:
            if reserva is reserva_excluir:
                continue
            if reserva.servicio.identificador != self.identificador:
                continue
            if reserva.estado not in ESTADOS_QUE_OCUPAN_RECURSO:
                continue
            if _hay_cruce(fecha_inicio, fecha_fin, reserva.fecha_inicio, reserva.fecha_fin):
                ocupados += reserva.parametros.get("cantidad", 1)
        if ocupados + solicitados > self.cantidad_disponible:
            disponibles = self.cantidad_disponible - ocupados
            raise ServicioNoDisponibleError(
                f"Inventario insuficiente para {self.identificador}. "
                f"Unidades disponibles en ese período: {disponibles}."
            )

    def describir_servicio(self):
        return (
            f"Equipo | Código: {self.identificador} | {self.nombre} | "
            f"Tarifa: ${self.tarifa:,.0f}/equipo/día COP | "
            f"Inventario: {self.cantidad_disponible}"
        )


class ServicioAsesoria(Servicio):
    """Asesoría asignada a un especialista, con agenda individual."""

    UNIDAD_DURACION = "horas"

    def __init__(self, identificador, nombre, especialista, tarifa=TARIFA_ASESORIA_POR_HORA):
        self._especialista = especialista.strip() if isinstance(especialista, str) else especialista
        super().__init__(identificador, nombre, tarifa)
        self.validar_datos()

    @property
    def especialista(self):
        return self._especialista

    def validar_datos(self):
        super().validar_datos()
        if not isinstance(self._especialista, str) or len(self._especialista.strip()) < 3:
            raise ServicioInvalidoError("Debe indicar el nombre del especialista.")

    def validar_parametros(self, duracion, parametros=None):
        self._validar_duracion(duracion)
        datos = dict(parametros or {})
        if datos:
            raise ServicioInvalidoError("La asesoría no admite parámetros adicionales.")
        return datos

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **parametros):
        self.validar_parametros(duracion, parametros)
        base = self.tarifa * self._validar_duracion(duracion)
        return self._aplicar_impuestos_descuentos(base, impuesto, descuento)

    def verificar_disponibilidad(self, fecha_inicio, fecha_fin, reservas, parametros=None, reserva_excluir=None):
        if not self.activo:
            raise ServicioNoDisponibleError(f"El servicio {self.identificador} está inactivo.")
        self.validar_parametros(1, parametros)
        for reserva in reservas:
            if reserva is reserva_excluir:
                continue
            if reserva.servicio.identificador != self.identificador:
                continue
            if reserva.estado not in ESTADOS_QUE_OCUPAN_RECURSO:
                continue
            if _hay_cruce(fecha_inicio, fecha_fin, reserva.fecha_inicio, reserva.fecha_fin):
                raise ServicioNoDisponibleError(
                    f"El especialista {self.especialista} ya tiene una asesoría en ese horario."
                )

    def describir_servicio(self):
        return (
            f"Asesoría | Código: {self.identificador} | {self.nombre} | "
            f"Especialista: {self.especialista} | "
            f"Tarifa: ${self.tarifa:,.0f}/hora COP"
        )
