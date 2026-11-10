estudiante : mauricio alberto velasco
"""Simulación automática de 12 operaciones de Software FJ.


Usa el mismo SistemaSoftwareFJ del proyecto. Cada operación se ejecuta de forma
protegida: si falla, el error se registra en el log y la simulación continúa.
Se llama desde el menú (opción 11) o directamente: python simulacion.py
"""
from datetime import datetime
from decimal import Decimal

from configuracion import FORMATO_FECHA_HORA
from excepciones.errores import ErrorSoftwareFJ
from gestion.sistema import SistemaSoftwareFJ, configurar_logger

logger = configurar_logger()  # Mismo logger que usa el resto del sistema


def fecha(texto):
    """Convierte 'AAAA-MM-DD HH:MM' en datetime usando el formato del proyecto."""
    return datetime.strptime(texto, FORMATO_FECHA_HORA)


def ejecutar(numero, titulo, operacion):
    """Ejecuta una operación con try/except/else/finally sin detener la simulación."""
    print(f"\n[{numero:02d}] {titulo}")
    try:
        resultado = operacion()  # Se intenta la operación
    except ErrorSoftwareFJ as exc:
        # Error controlado del dominio: se registra y se continúa
        logger.error("Simulación %s (%s) falló: %s", numero, titulo, exc)
        print(f"     ERROR controlado -> {type(exc).__name__}: {exc}")
    except (ValueError, TypeError) as exc:
        # Datos de entrada inválidos
        logger.error("Simulación %s (%s) datos inválidos: %s", numero, titulo, exc)
        print(f"     DATOS INVÁLIDOS -> {exc}")
    except Exception as exc:
        # Cualquier error inesperado
        logger.exception("Simulación %s error inesperado: %s", numero, exc)
        print(f"     ERROR inesperado -> {type(exc).__name__}: {exc}")
    else:
        logger.info("Simulación %s (%s) exitosa.", numero, titulo)
        print(f"     OK -> {resultado}")
    finally:
        logger.info("Simulación %s finalizada.", numero)


def ejecutar_simulacion():
    """Corre las 12 operaciones y muestra el resumen final."""
    s = SistemaSoftwareFJ()
    print("=== SIMULACIÓN SOFTWARE FJ (12 operaciones) ===")

    # --- Clientes: válidos e inválidos ---
    ejecutar(1, "Registrar cliente válido",
             lambda: s.registrar_cliente("1001", "Ana María Gómez", "ana@correo.com", "3001234567").describir())
    ejecutar(2, "Registrar cliente con correo inválido",
             lambda: s.registrar_cliente("1002", "Luis Pérez", "luis#correo", "3109876543"))
    ejecutar(3, "Registrar cliente con identificación duplicada",
             lambda: s.registrar_cliente("1001", "Otra Persona", "otra@correo.com", "3112223344"))

    # --- Servicios: correctos e incorrectos ---
    ejecutar(4, "Crear servicio de sala válido",
             lambda: s.crear_servicio_sala("S01", "Sala Ejecutiva", None, 20).describir_servicio())
    ejecutar(5, "Crear servicio de equipo con inventario inválido",
             lambda: s.crear_servicio_equipo("E01", "Proyectores", None, -3))
    ejecutar(6, "Crear servicio de asesoría válido",
             lambda: s.crear_servicio_asesoria("A01", "Asesoría en software", "Carlos Ruiz", None).describir_servicio())
    ejecutar(7, "Crear servicio de equipo válido",
             lambda: s.crear_servicio_equipo("E02", "Portátiles", None, 10).describir_servicio())

    # --- Reservas: exitosas y fallidas ---
    ejecutar(8, "Crear y confirmar reserva de sala",
             lambda: _crear_y_confirmar(s, "R01", "1001", "S01", "2026-12-01 09:00", Decimal("3"), {"personas": 10}))
    ejecutar(9, "Reserva de sala con más personas que la capacidad",
             lambda: s.crear_reserva("R02", "1001", "S01", fecha("2026-12-02 09:00"), Decimal("2"), {"personas": 50}))
    ejecutar(10, "Procesar reserva confirmada con impuesto y descuento",
             lambda: f"Total: ${s.procesar_reserva('R01', impuesto=Decimal('0.19'), descuento=Decimal('0.10')):,.2f} COP")
    ejecutar(11, "Cancelar una reserva ya procesada",
             lambda: s.cancelar_reserva("R01"))
    ejecutar(12, "Reserva para un cliente inexistente",
             lambda: s.crear_reserva("R03", "9999", "S01", fecha("2026-12-03 09:00"), Decimal("1"), {"personas": 5}))

    # --- Resumen final: el sistema siguió operando pese a los errores ---
    resumen = s.resumen()
    print("\n=== RESUMEN ===")
    print(f"Clientes: {resumen['clientes']} | Servicios: {resumen['servicios']} | Reservas: {resumen['reservas']}")
    print(f"Total procesado: ${resumen['total_procesado']:,.2f} COP")


def _crear_y_confirmar(sistema, codigo, cliente, servicio, inicio, duracion, parametros):
    """Crea una reserva y la confirma; devuelve su descripción."""
    reserva = sistema.crear_reserva(codigo, cliente, servicio, fecha(inicio), duracion, parametros)
    sistema.confirmar_reserva(codigo)
    return reserva.describir()


if __name__ == "__main__":
    ejecutar_simulacion()
