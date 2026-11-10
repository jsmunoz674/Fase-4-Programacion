"""Configuración central del sistema Software FJ.

Las tarifas son valores ilustrativos en pesos colombianos (COP) y pueden
modificarse aquí sin cambiar las clases que realizan los cálculos.
"""
from decimal import Decimal
from pathlib import Path

RUTA_PROYECTO = Path(__file__).resolve().parent
RUTA_REGISTROS = RUTA_PROYECTO / "registros"
RUTA_REGISTROS.mkdir(parents=True, exist_ok=True)
RUTA_LOG = RUTA_REGISTROS / "software_fj.log"

""" Tarifas de referencia (COP). No representan precios comerciales reales"""
TARIFA_SALA_POR_HORA = Decimal("45000")
TARIFA_EQUIPO_POR_DIA = Decimal("30000")
TARIFA_ASESORIA_POR_HORA = Decimal("80000")

"""Valores predeterminados para impuestos y límites de validación."""
IMPUESTO_PREDETERMINADO = Decimal("0.19")
DESCUENTO_MAXIMO = Decimal("1.00")

FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M"
