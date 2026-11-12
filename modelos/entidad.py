"""Clase abstracta común para las entidades principales del sistema."""
from abc import ABC, abstractmethod

from excepciones.errores import DatosInvalidosError


class EntidadSistema(ABC):
    """Representa una entidad identificable dentro de Software FJ."""

    def __init__(self, identificador: str):
        if not isinstance(identificador, str) or not identificador.strip():
            raise DatosInvalidosError("El identificador es obligatorio.")
        self._identificador = identificador.strip().upper()

    @property
    def identificador(self) -> str:
        """Devuelve el identificador sin permitir modificarlo directamente."""
        return self._identificador

    @abstractmethod
    def validar_datos(self) -> None:
        """Cada entidad implementa sus propias reglas de validación."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""
