"""Clase abstracta Servicio y reglas compartidas por sus especializaciones."""
from abc import abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from math import isfinite

from modelos.entidad import EntidadSistema
from excepciones.errores import ServicioInvalidoError


class Servicio(EntidadSistema):
    """Plantilla abstracta para los servicios ofrecidos por Software FJ.

    calcular_costo() acepta parámetros opcionales de impuesto y descuento.
    Esta es la forma de simular sobrecarga en Python mediante argumentos
    predeterminados, ya que Python no sobrecarga métodos por firma como Java.
    """

    UNIDAD_DURACION = "unidades"

    def __init__(self, identificador: str, nombre: str, tarifa, activo: bool = True):
        super().__init__(identificador)
        self._nombre = nombre.strip() if isinstance(nombre, str) else nombre
        self._tarifa = self._convertir_decimal(tarifa, "La tarifa")
        self._activo = bool(activo)
        self.validar_datos()

    @staticmethod
    def _convertir_decimal(valor, etiqueta: str) -> Decimal:
        try:
            numero = Decimal(str(valor))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ServicioInvalidoError(f"{etiqueta} debe ser numérica.") from exc
        if not numero.is_finite():
            raise ServicioInvalidoError(f"{etiqueta} debe ser un número finito.")
        return numero

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa(self) -> Decimal:
        return self._tarifa

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        self._activo = False

    def activar(self) -> None:
        self._activo = True

    def validar_datos(self) -> None:
        if not isinstance(self._nombre, str) or len(self._nombre.strip()) < 3:
            raise ServicioInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        if self._tarifa <= 0:
            raise ServicioInvalidoError("La tarifa debe ser mayor que cero.")

    def _validar_duracion(self, duracion) -> Decimal:
        try:
            valor = Decimal(str(duracion))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ServicioInvalidoError("La duración debe ser numérica.") from exc
        if not valor.is_finite() or valor <= 0:
            raise ServicioInvalidoError("La duración debe ser un número positivo y finito.")
        return valor

    def calcular_fecha_fin(self, fecha_inicio: datetime, duracion) -> datetime:
        if not isinstance(fecha_inicio, datetime):
            raise ServicioInvalidoError("La fecha de inicio debe ser un objeto datetime.")
        duracion_decimal = self._validar_duracion(duracion)
        duracion_float = float(duracion_decimal)
        if not isfinite(duracion_float):
            raise ServicioInvalidoError("La duración está fuera del rango permitido.")
        if self.UNIDAD_DURACION == "dias":
            return fecha_inicio + timedelta(days=duracion_float)
        return fecha_inicio + timedelta(hours=duracion_float)

    def _aplicar_impuestos_descuentos(self, costo_base, impuesto=0, descuento=0) -> Decimal:
        base = self._convertir_decimal(costo_base, "El costo base")
        tasa_impuesto = self._convertir_decimal(impuesto, "El impuesto")
        tasa_descuento = self._convertir_decimal(descuento, "El descuento")
        if base < 0:
            raise ServicioInvalidoError("El costo base no puede ser negativo.")
        if not Decimal("0") <= tasa_impuesto <= Decimal("1"):
            raise ServicioInvalidoError("El impuesto debe estar entre 0 y 1 (0 % a 100 %).")
        if not Decimal("0") <= tasa_descuento <= Decimal("1"):
            raise ServicioInvalidoError("El descuento debe estar entre 0 y 1 (0 % a 100 %).")
        total = base * (Decimal("1") - tasa_descuento) * (Decimal("1") + tasa_impuesto)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @abstractmethod
    def validar_parametros(self, duracion, parametros=None) -> dict:
        """Valida parámetros específicos de cada servicio."""

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0, **parametros) -> Decimal:
        """Calcula el costo de acuerdo con la especialización del servicio."""

    @abstractmethod
    def verificar_disponibilidad(
        self, fecha_inicio, fecha_fin, reservas, parametros=None, reserva_excluir=None
    ) -> None:
        """Lanza ServicioNoDisponibleError cuando el recurso no está disponible."""

    @abstractmethod
    def describir_servicio(self) -> str:
        """Devuelve la descripción específica del servicio."""

    def describir(self) -> str:
        return self.describir_servicio()

    def __str__(self) -> str:
        return self.describir_servicio()
