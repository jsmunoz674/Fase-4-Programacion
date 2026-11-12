# Revisión del proyecto Software FJ (etapa 7)

Lista de verificación de lo que pide el enunciado del Ejercicio 1 frente a lo que hay hoy en el repositorio.
Los puntos marcados como **Por verificar** dependen de código que todavía no está subido (`gestion/sistema.py` y los archivos de `modelos/`).

## 1. Requisitos del enunciado

| Requisito | Evidencia en el repositorio | Estado |
|---|---|---|
| Programación orientada a objetos, sin base de datos | `main.py` indica que los datos se conservan en memoria durante la sesión | Por verificar |
| Clase abstracta de entidades generales (`EntidadSistema`) | `modelos/entidad.py` | Por verificar |
| Clase `Cliente` con validaciones y encapsulación | `modelos/cliente.py` | Por verificar |
| Clase abstracta `Servicio` y al menos tres servicios especializados | `main.py` importa `ServicioSala`, `ServicioEquipo` y `ServicioAsesoria` | Por verificar |
| Polimorfismo y métodos sobrescritos (costos, descripción, validación) | `modelos/servicios_especializados.py` | Por verificar |
| Métodos sobrecargados (impuestos, descuentos, parámetros opcionales) | `modelos/` | Por verificar |
| Clase `Reserva` (cliente, servicio, duración, estado; confirmar, cancelar, procesar) | `modelos/reserva.py` | Por verificar |
| Excepciones personalizadas | `exepciones/errores.py` (jerarquía a partir de `ErrorSoftwareFJ`) | Cumple |
| `try/except`, `try/except/else`, `try/except/finally` | `main.py` (`ejecutar_menu`) | Cumple |
| Encadenamiento de excepciones (`raise ... from`) | `main.py` (`leer_numero`, `leer_entero`, `leer_fecha_hora`) | Cumple |
| Archivo de logs con errores y eventos | `configuracion.py` define `RUTA_LOG`; existe `registros/software_fj.log` | Por verificar (el log está vacío) |
| Tarifas y configuración | `configuracion.py` | Cumple |
| Menú interactivo por consola | `main.py` (10 opciones y salir) | Cumple |
| Al menos 10 operaciones válidas e inválidas | `simulacion.py` (12 operaciones) | Por verificar (falta ejecutarla con el sistema real) |

## 2. Observaciones encontradas

1. La carpeta se llama `exepciones` (sin la "c") y su archivo de inicio `_init_.py` (con un solo guion bajo por lado). `main.py` importa `excepciones.errores`, por lo que Python no encuentra el módulo. Debe quedar como `excepciones/__init__.py`.
2. El encabezado de `main.py` menciona "Tarea 2 Ejercicio 4 Control de Computadores en Mantenimiento", que corresponde a otra tarea.
3. `main.py` importa `logging` y `Reserva`, pero no los usa.
4. En `leer_numero`, `Decimal` acepta valores como `NaN` o `Infinity`. Se puede validar con `is_finite()`.
5. Varios comentarios están escritos como cadenas `"""..."""` antes de la función. Conviene moverlos dentro como docstrings.
6. El mensaje del bloque `finally` dice "operación finalizado"; debería decir "finalizada".
7. El README propone 13 operaciones; `simulacion.py` tiene 12. El enunciado exige al menos 10.

## 3. Pendiente de comprobar cuando se suba el código completo

- Ejecutar `python main.py` y recorrer las 10 opciones del menú.
- Ejecutar `python simulacion.py` y confirmar que corre sin interrupciones.
- Revisar que el archivo de logs registre los errores y eventos.
- Confirmar que cada línea de código esté documentada.
