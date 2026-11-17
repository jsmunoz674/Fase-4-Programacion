"""Clase Cliente: datos personales encapsulados y validados."""
import re  # Expresiones regulares para validar nombre y correo

from excepciones.errores import ClienteInvalidoError, DatosInvalidosError
from modelos.entidad import EntidadSistema

# Patrones de validación reutilizables
_PATRON_IDENTIFICACION = re.compile(r"[A-Za-z0-9]{4,15}")
_PATRON_NOMBRE = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,80}")
_PATRON_CORREO = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")


class Cliente(EntidadSistema):
    """Cliente de Software FJ con sus datos personales protegidos."""

    def __init__(self, identificacion, nombre, correo, telefono):
        # La clase base valida y normaliza el identificador; se traduce su error
        try:
            super().__init__(identificacion)
        except DatosInvalidosError as exc:
            # Encadenamiento: se conserva la causa original con "from exc"
            raise ClienteInvalidoError("La identificación del cliente es obligatoria.") from exc
        # Los datos personales son privados y se asignan por propiedades (con validación)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        # Validación final del objeto completo
        self.validar_datos()

    # ---------- identificación ----------
    def _validar_identificacion(self) -> None:
        """La identificación debe tener entre 4 y 15 letras o números."""
        if not _PATRON_IDENTIFICACION.fullmatch(self.identificador):
            raise ClienteInvalidoError(f"Identificación inválida: '{self.identificador}'.")

    # ---------- nombre ----------
    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor) -> None:
        valor = str(valor).strip() if valor is not None else ""
        if not _PATRON_NOMBRE.fullmatch(valor):
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}'. Use solo letras (mínimo 3).")
        self._nombre = valor.title()  # Se guarda con formato "Nombre Apellido"

    # ---------- correo ----------
    @property
    def correo(self) -> str:
        """Correo electrónico del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor) -> None:
        valor = str(valor).strip().lower() if valor is not None else ""
        if not _PATRON_CORREO.fullmatch(valor):
            raise ClienteInvalidoError(f"Correo inválido: '{valor}'.")
        self._correo = valor

    # ---------- teléfono ----------
    @property
    def telefono(self) -> str:
        """Teléfono del cliente (solo dígitos)."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor) -> None:
        valor = str(valor).strip() if valor is not None else ""
        if not (valor.isdigit() and 7 <= len(valor) <= 10):
            raise ClienteInvalidoError(f"Teléfono inválido: '{valor}'. Use de 7 a 10 dígitos.")
        self._telefono = valor

    # ---------- métodos de la clase abstracta ----------
    def validar_datos(self) -> None:
        """Implementa la regla de validación exigida por EntidadSistema."""
        self._validar_identificacion()
        # Reasignar ejecuta de nuevo las validaciones de cada propiedad
        self.nombre = self._nombre
        self.correo = self._correo
        self.telefono = self._telefono

    def describir(self) -> str:
        """Descripción legible del cliente."""
        return (f"Cliente {self.identificador}: {self.nombre} "
                f"<{self.correo}> Tel: {self.telefono}")

    def __str__(self) -> str:
        # Permite imprimir el cliente directamente con print()
        return self.describir()
