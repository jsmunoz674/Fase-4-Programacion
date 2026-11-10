"""Tarea 2 Ejercicio 4 Control de Computadores en Mantenimiento"""
"""Estudiante 1 :Juan Sebastian Muñoz Lopez"""
"""Curso: Programación Código: 213023"""
"""Punto de entrada de Software FJ. se inicializa creando  el main.py con la estructura propuesta para el desarrolo del menu y sus modulos"""
from datetime import datetime
from decimal import Decimal
import logging

from configuracion import FORMATO_FECHA_HORA
from excepciones.errores import ErrorSoftwareFJ
from gestion.sistema import SistemaSoftwareFJ, configurar_logger
from modelos.reserva import Reserva
from modelos.servicios_especializados import ServicioSala, ServicioEquipo, ServicioAsesoria


logger = configurar_logger()


def leer_texto(mensaje):
    valor = input(mensaje).strip()
    if not valor:
        raise ValueError("El campo no puede quedar vacío.")
    return valor


def leer_numero(mensaje, permitir_vacio=False, predeterminado=None):
    texto = input(mensaje).strip()
    if permitir_vacio and not texto:
        return predeterminado
    try:
        return Decimal(texto)
    except Exception as exc:
        raise ValueError("Debe ingresar un valor numérico válido.") from exc


def leer_entero(mensaje):
    texto = input(mensaje).strip()
    try:
        return int(texto)
    except ValueError as exc:
        raise ValueError("Debe ingresar un número entero.") from exc


def leer_fecha_hora(mensaje="Fecha y hora (AAAA-MM-DD HH:MM): "):
    texto = leer_texto(mensaje)
    try:
        return datetime.strptime(texto, FORMATO_FECHA_HORA)
    except ValueError as exc:
        raise ValueError(
            f"Fecha inválida. Utilice el formato {FORMATO_FECHA_HORA}."
        ) from exc

"""Menu del programa"""
def mostrar_menu():
    print("\n" + "=" * 62)
    print("                 SOFTWARE FJ - GESTIÓN INTEGRAL")
    print("=" * 62)
    print("1. Registrar cliente")
    print("2. Listar clientes")
    print("3. Crear servicio")
    print("4. Listar servicios")
    print("5. Crear reserva")
    print("6. Confirmar reserva")
    print("7. Cancelar reserva")
    print("8. Procesar reserva y calcular costo")
    print("9. Listar reservas")
    print("10. Mostrar resumen del sistema")
    print("0. Salir")
    print("-" * 62)

"""Regristro de cliente"""
def registrar_cliente(sistema):
    print("\n--- REGISTRO DE CLIENTE ---")
    cliente = sistema.registrar_cliente(
        leer_texto("Identificación: "),
        leer_texto("Nombre completo: "),
        leer_texto("Correo electrónico: "),
        leer_texto("Teléfono: "),
    )
    print(f"Cliente registrado: {cliente.describir()}")

"""Creacion del servicio"""
def crear_servicio(sistema):
    print("\n--- CREACIÓN DE SERVICIO ---")
    print("1. Reserva de sala")
    print("2. Alquiler de equipos")
    print("3. Asesoría especializada")
    tipo = leer_texto("Seleccione el tipo: ")
    codigo = leer_texto("Código del servicio: ")
    nombre = leer_texto("Nombre o descripción: ")

    if tipo == "1":
        tarifa = leer_numero("Tarifa por hora COP (Enter para usar estándar): ", True, None)
        capacidad = leer_entero("Capacidad máxima de personas: ")
        servicio = sistema.crear_servicio_sala(codigo, nombre, tarifa, capacidad)
    elif tipo == "2":
        tarifa = leer_numero("Tarifa por equipo/día COP (Enter para usar estándar): ", True, None)
        inventario = leer_entero("Cantidad total de equipos disponibles: ")
        servicio = sistema.crear_servicio_equipo(codigo, nombre, tarifa, inventario)
    elif tipo == "3":
        especialista = leer_texto("Nombre del especialista: ")
        tarifa = leer_numero("Tarifa por hora COP (Enter para usar estándar): ", True, None)
        servicio = sistema.crear_servicio_asesoria(codigo, nombre, especialista, tarifa)
    else:
        raise ValueError("Tipo de servicio no reconocido.")

    print(f"Servicio registrado: {servicio.describir_servicio()}")

"""Creacion de  la reserva"""
def crear_reserva(sistema):
    print("\n--- CREACIÓN DE RESERVA ---")
    codigo_reserva = leer_texto("Código de reserva: ")
    identificacion = leer_texto("Identificación del cliente: ")
    codigo_servicio = leer_texto("Código del servicio: ")
    servicio = sistema.buscar_servicio(codigo_servicio)
    fecha_inicio = leer_fecha_hora()
    if servicio.UNIDAD_DURACION == "dias":
        duracion = leer_numero("Duración en días: ")
    else:
        duracion = leer_numero("Duración en horas: ")

    parametros = {}
    if isinstance(servicio, ServicioSala):
        parametros["personas"] = leer_entero("Cantidad de personas: ")
    elif isinstance(servicio, ServicioEquipo):
        parametros["cantidad"] = leer_entero("Cantidad de equipos solicitados: ")

    reserva = sistema.crear_reserva(
        codigo_reserva, identificacion, codigo_servicio,
        fecha_inicio, duracion, parametros
    )
    print(f"Reserva creada en estado {reserva.estado}.")
    print(reserva.describir())

"""Procesamiento de la recerva y calculo del costo"""
def procesar_reserva(sistema):
    print("\n--- PROCESAMIENTO DE RESERVA ---")
    codigo = leer_texto("Código de reserva confirmada: ")
    impuesto_pct = leer_numero("Impuesto en porcentaje (Enter para 19): ", True, Decimal("19"))
    descuento_pct = leer_numero("Descuento en porcentaje (Enter para 0): ", True, Decimal("0"))
    if not Decimal("0") <= impuesto_pct <= Decimal("100"):
        raise ValueError("El impuesto debe estar entre 0 y 100 por ciento.")
    if not Decimal("0") <= descuento_pct <= Decimal("100"):
        raise ValueError("El descuento debe estar entre 0 y 100 por ciento.")

    total = sistema.procesar_reserva(
        codigo,
        impuesto=impuesto_pct / Decimal("100"),
        descuento=descuento_pct / Decimal("100"),
    )
    print(f"Reserva procesada. Total: ${total:,.2f} COP")

"""print de error de no recervas disponibles"""
def mostrar_lista(titulo, elementos):
    print(f"\n--- {titulo} ---")
    if not elementos:
        print("No hay registros disponibles.")
        return
    for elemento in elementos:
        print(elemento)

"""Mensaje de inicializacion del programa"""
def ejecutar_menu():
    sistema = SistemaSoftwareFJ()
    print("Software FJ iniciado. Los datos se conservan en memoria durante esta sesión.")
    

    while True:
        mostrar_menu()
        try:
            opcion = input("Seleccione una opción: ").strip()
            if opcion == "0":
                print("Cerrando Software FJ. ¡Hasta pronto!")
                break
            elif opcion == "1":
                registrar_cliente(sistema)
            elif opcion == "2":
                mostrar_lista("CLIENTES", sistema.listar_clientes())
            elif opcion == "3":
                crear_servicio(sistema)
            elif opcion == "4":
                mostrar_lista("SERVICIOS", sistema.listar_servicios())
            elif opcion == "5":
                crear_reserva(sistema)
            elif opcion == "6":
                reserva = sistema.confirmar_reserva(leer_texto("Código de reserva: "))
                print(f"Reserva {reserva.identificador} confirmada.")
            elif opcion == "7":
                reserva = sistema.cancelar_reserva(leer_texto("Código de reserva: "))
                print(f"Reserva {reserva.identificador} cancelada.")
            elif opcion == "8":
                procesar_reserva(sistema)
            elif opcion == "9":
                mostrar_lista("RESERVAS", sistema.listar_reservas())
            elif opcion == "10":
                resumen = sistema.resumen()
                print("\n--- RESUMEN SOFTWARE FJ ---")
                print(f"Clientes registrados: {resumen['clientes']}")
                print(f"Servicios registrados: {resumen['servicios']}")
                print(f"Reservas registradas: {resumen['reservas']}")
                for estado, cantidad in resumen["estados"].items():
                    print(f"Reservas {estado.lower()}: {cantidad}")
                print(f"Total procesado: ${resumen['total_procesado']:,.2f} COP")
            else:
                raise ValueError("Opción no válida. Seleccione una opción del menú.")
        except ErrorSoftwareFJ as exc:
            logger.exception("Error controlado en el menú: %s", exc)
            print(f"\n[ERROR CONTROLADO] {exc}")
        except (ValueError, TypeError) as exc:
            logger.exception("Entrada inválida en el menú: %s", exc)
            print(f"\n[DATOS INVÁLIDOS] {exc}")
        except Exception as exc:
            logger.exception("Error inesperado en el menú: %s", exc)
            print("\n[ERROR INESPERADO] La operación no pudo completarse. El sistema continúa activo.")
        else:
            print("\nOperación atendida.")
        finally:
            print("operación finalizado; Software FJ permanece disponible.")


if __name__ == "__main__":
    ejecutar_menu()
