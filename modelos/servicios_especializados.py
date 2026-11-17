"""Servicios concretos: sala, alquiler de equipos y asesoría especializada.

Cada servicio calcula su costo y aplica una política de disponibilidad diferente.
"""
from datetime import datetime

from configuracion import (
    TARIFA_ASESORIA_POR_HORA,
    TARIFA_EQUIPO_POR_DIA,
    TARIFA_SALA_POR_HORA,
)
from excepciones.errores import ServicioInvalidoError, ServicioNoDisponibleError
from modelos.servicio import Servicio


def _entero_positivo(valor, nombre):
    """Acepta enteros positivos, pero no booleanos ni fracciones."""
    if isinstance(valor, bool) or not str(valor).isdigit() or int(valor) <= 0:
        raise ServicioInvalidoError(f"{nombre} debe ser un entero mayor que cero.")
    return int(valor)


def _parametros_como_diccionario(parametros):
    if parametros is None:
        return {}
    if not isinstance(parametros, dict):
        raise ServicioInvalidoError("Los parámetros deben ser un diccionario.")
    return dict(parametros)


def _verificar_intervalo(fecha_inicio, fecha_fin):
    if not isinstance(fecha_inicio, datetime) or not isinstance(fecha_fin, datetime):
        raise ServicioInvalidoError("Las fechas deben ser objetos datetime.")
    try:
        correcto = fecha_inicio < fecha_fin
    except TypeError as exc:
        raise ServicioInvalidoError("Las fechas deben usar el mismo tipo de zona horaria.") from exc
    if not correcto:
        raise ServicioInvalidoError("La fecha final debe ser posterior a la inicial.")


def _se_superponen(inicio_a, fin_a, inicio_b, fin_b):
    """Los intervalos consecutivos no se consideran superpuestos."""
    return inicio_a < fin_b and inicio_b < fin_a


def _reservas_que_ocupan(reservas, fecha_inicio, fecha_fin, reserva_excluir):
    """Las reservas canceladas liberan cupo; las finalizadas conservan historial."""
    for reserva in reservas:
        if reserva is reserva_excluir or reserva.estado == "CANCELADA":
            continue
        if _se_superponen(fecha_inicio, fecha_fin,
                         reserva.fecha_inicio, reserva.fecha_fin):
            yield reserva


class ServicioSala(Servicio):
    """Reserva una sala completa; su capacidad limita asistentes, no reservas."""
    UNIDAD_DURACION = "horas"

    def __init__(self, identificador, nombre, tarifa=TARIFA_SALA_POR_HORA,
                 capacidad=12, activo=True):
        self._capacidad = _entero_positivo(capacidad, "La capacidad")
        super().__init__(identificador, nombre, tarifa, activo)

    @property
    def capacidad(self):
        return self._capacidad

    def validar_datos(self):
        super().validar_datos()
        _entero_positivo(self._capacidad, "La capacidad")

    def validar_parametros(self, duracion, parametros=None):
        self._validar_duracion(duracion)
        datos = _parametros_como_diccionario(parametros)
        personas = _entero_positivo(datos.get("personas"), "La cantidad de personas")
        if personas > self.capacidad:
            raise ServicioInvalidoError(
                f"La sala permite máximo {self.capacidad} personas."
            )
        return {"personas": personas}

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **parametros):
        self.validar_parametros(duracion, parametros)
        base = self.tarifa * self._validar_duracion(duracion)
        return self._aplicar_impuestos_descuentos(base, impuesto, descuento)

    def verificar_disponibilidad(self, fecha_inicio, fecha_fin, reservas,
                                 parametros=None, reserva_excluir=None):
        _verificar_intervalo(fecha_inicio, fecha_fin)
        self.validar_parametros(1, parametros)
        if not self.activo:
            raise ServicioNoDisponibleError("La sala está inactiva.")
        if any(reserva.servicio.identificador == self.identificador
               for reserva in _reservas_que_ocupan(
                   reservas, fecha_inicio, fecha_fin, reserva_excluir)):
            raise ServicioNoDisponibleError("La sala ya está reservada para ese horario.")

    def describir_servicio(self):
        return (f"Sala {self.identificador}: {self.nombre} | "
                f"capacidad {self.capacidad} | ${self.tarifa:,.2f} COP/hora")


class ServicioEquipo(Servicio):
    """Alquiler de equipos por día con inventario compartido por intervalo."""
    UNIDAD_DURACION = "dias"

    def __init__(self, identificador, nombre, tarifa=TARIFA_EQUIPO_POR_DIA,
                 cantidad_disponible=10, activo=True):
        self._cantidad_disponible = _entero_positivo(
            cantidad_disponible, "La cantidad disponible"
        )
        super().__init__(identificador, nombre, tarifa, activo)

    @property
    def cantidad_disponible(self):
        return self._cantidad_disponible

    def validar_datos(self):
        super().validar_datos()
        _entero_positivo(self._cantidad_disponible, "La cantidad disponible")

    def validar_parametros(self, duracion, parametros=None):
        self._validar_duracion(duracion)
        datos = _parametros_como_diccionario(parametros)
        cantidad = _entero_positivo(datos.get("cantidad"), "La cantidad de equipos")
        if cantidad > self.cantidad_disponible:
            raise ServicioInvalidoError(
                f"Solo hay {self.cantidad_disponible} equipos en inventario."
            )
        return {"cantidad": cantidad}

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **parametros):
        datos = self.validar_parametros(duracion, parametros)
        base = self.tarifa * self._validar_duracion(duracion) * datos["cantidad"]
        return self._aplicar_impuestos_descuentos(base, impuesto, descuento)

    def verificar_disponibilidad(self, fecha_inicio, fecha_fin, reservas,
                                 parametros=None, reserva_excluir=None):
        _verificar_intervalo(fecha_inicio, fecha_fin)
        datos = self.validar_parametros(1, parametros)
        if not self.activo:
            raise ServicioNoDisponibleError("El servicio de equipos está inactivo.")
        ocupados = sum(
            reserva.parametros["cantidad"]
            for reserva in _reservas_que_ocupan(
                reservas, fecha_inicio, fecha_fin, reserva_excluir)
            if reserva.servicio.identificador == self.identificador
        )
        if ocupados + datos["cantidad"] > self.cantidad_disponible:
            restantes = self.cantidad_disponible - ocupados
            raise ServicioNoDisponibleError(
                f"Inventario insuficiente para ese horario: {restantes} disponibles."
            )

    def describir_servicio(self):
        return (f"Equipos {self.identificador}: {self.nombre} | "
                f"inventario {self.cantidad_disponible} | "
                f"${self.tarifa:,.2f} COP/equipo/día")


class ServicioAsesoria(Servicio):
    """Asesoría por horas: un especialista no puede atender dos citas a la vez."""
    UNIDAD_DURACION = "horas"

    def __init__(self, identificador, nombre, especialista,
                 tarifa=TARIFA_ASESORIA_POR_HORA, activo=True):
        self._especialista = especialista.strip() if isinstance(especialista, str) else ""
        super().__init__(identificador, nombre, tarifa, activo)

    @property
    def especialista(self):
        return self._especialista

    def validar_datos(self):
        super().validar_datos()
        if len(self._especialista) < 3:
            raise ServicioInvalidoError("El especialista debe tener al menos 3 caracteres.")

    def validar_parametros(self, duracion, parametros=None):
        self._validar_duracion(duracion)
        datos = _parametros_como_diccionario(parametros)
        if datos:
            raise ServicioInvalidoError("La asesoría no requiere parámetros adicionales.")
        return {}

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **parametros):
        self.validar_parametros(duracion, parametros)
        base = self.tarifa * self._validar_duracion(duracion)
        return self._aplicar_impuestos_descuentos(base, impuesto, descuento)

    def verificar_disponibilidad(self, fecha_inicio, fecha_fin, reservas,
                                 parametros=None, reserva_excluir=None):
        _verificar_intervalo(fecha_inicio, fecha_fin)
        self.validar_parametros(1, parametros)
        if not self.activo:
            raise ServicioNoDisponibleError("La asesoría está inactiva.")
        if any(
            isinstance(reserva.servicio, ServicioAsesoria)
            and reserva.servicio.especialista.casefold() == self.especialista.casefold()
            for reserva in _reservas_que_ocupan(
                reservas, fecha_inicio, fecha_fin, reserva_excluir)
        ):
            raise ServicioNoDisponibleError(
                "El especialista ya tiene una asesoría en ese horario."
            )

    def describir_servicio(self):
        return (f"Asesoría {self.identificador}: {self.nombre} | "
                f"especialista {self.especialista} | ${self.tarifa:,.2f} COP/hora")
