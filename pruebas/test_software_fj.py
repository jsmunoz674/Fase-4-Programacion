"""Pruebas básicas e integrales con unittest, sin dependencias externas."""
from datetime import datetime, timedelta
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from excepciones.errores import (
    ClienteDuplicadoError,
    ClienteInvalidoError,
    OperacionNoPermitidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from gestion.sistema import SistemaSoftwareFJ
from main import leer_numero


class TestSoftwareFJ(TestCase):
    def setUp(self):
        self.sistema = SistemaSoftwareFJ()
        self.sistema.registrar_cliente(
            "1001", "Ana Maria Gomez", "ana@correo.com", "3001234567"
        )
        self.inicio = datetime(2026, 12, 1, 9)

    def test_cliente_valido_y_duplicado(self):
        self.assertEqual(self.sistema.clientes[0].identificador, "1001")
        with self.assertRaises(ClienteDuplicadoError):
            self.sistema.registrar_cliente(
                "1001", "Otra Persona", "otra@correo.com", "3001234567"
            )

    def test_cliente_rechaza_correo_invalido(self):
        with self.assertRaises(ClienteInvalidoError):
            self.sistema.registrar_cliente(
                "1002", "Luis Perez", "correo-invalido", "3001234567"
            )

    def test_sala_reserva_confirmacion_y_costo(self):
        self.sistema.crear_servicio_sala("S01", "Sala principal", capacidad=20)
        reserva = self.sistema.crear_reserva(
            "R01", "1001", "S01", self.inicio, 3, {"personas": 10}
        )
        self.assertEqual(reserva.estado, "PENDIENTE")
        self.sistema.confirmar_reserva("R01")
        total = self.sistema.procesar_reserva(
            "R01", impuesto=Decimal("0.19"), descuento=Decimal("0.10")
        )
        self.assertEqual(total, Decimal("144585.00"))
        self.assertEqual(reserva.estado, "FINALIZADA")
        self.assertEqual(self.sistema.resumen()["total_procesado"], total)

    def test_no_cancelar_reserva_finalizada(self):
        self.sistema.crear_servicio_sala("S01", "Sala principal")
        self.sistema.crear_reserva(
            "R01", "1001", "S01", self.inicio, 1, {"personas": 2}
        )
        self.sistema.confirmar_reserva("R01")
        self.sistema.procesar_reserva("R01")
        with self.assertRaises(OperacionNoPermitidaError):
            self.sistema.cancelar_reserva("R01")
        with self.assertRaises(OperacionNoPermitidaError):
            self.sistema.procesar_reserva("R01")

    def test_sala_no_admite_traslape_y_cancelacion_libera(self):
        self.sistema.crear_servicio_sala("S01", "Sala principal", capacidad=8)
        self.sistema.crear_reserva(
            "R01", "1001", "S01", self.inicio, 2, {"personas": 4}
        )
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva(
                "R02", "1001", "S01", self.inicio + timedelta(hours=1),
                2, {"personas": 2}
            )
        self.sistema.cancelar_reserva("R01")
        self.sistema.crear_reserva(
            "R02", "1001", "S01", self.inicio, 2, {"personas": 2}
        )
        self.assertEqual(len(self.sistema.reservas), 2)

    def test_sala_capacidad_invalida(self):
        self.sistema.crear_servicio_sala("S01", "Sala principal", capacidad=8)
        with self.assertRaises(ServicioInvalidoError):
            self.sistema.crear_reserva(
                "R01", "1001", "S01", self.inicio, 2, {"personas": 9}
            )

    def test_equipos_no_permite_superar_inventario(self):
        self.sistema.crear_servicio_equipo("E01", "Computadores", cantidad_disponible=5)
        self.sistema.crear_reserva(
            "R01", "1001", "E01", self.inicio, 2, {"cantidad": 3}
        )
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva(
                "R02", "1001", "E01", self.inicio + timedelta(days=1),
                1, {"cantidad": 3}
            )
        reserva = self.sistema.crear_reserva(
            "R03", "1001", "E01", self.inicio + timedelta(days=2),
            1, {"cantidad": 5}
        )
        self.assertEqual(reserva.fecha_fin, self.inicio + timedelta(days=3))
        self.sistema.confirmar_reserva("R01")
        self.assertEqual(self.sistema.procesar_reserva("R01"), Decimal("180000.00"))

    def test_asesoria_mismo_especialista_no_se_traslapa(self):
        self.sistema.crear_servicio_asesoria("A01", "Asesoria de redes", "Carlos Ruiz")
        self.sistema.crear_servicio_asesoria("A02", "Asesoria de seguridad", "Carlos Ruiz")
        self.sistema.crear_reserva(
            "R01", "1001", "A01", self.inicio, 2
        )
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva(
                "R02", "1001", "A02", self.inicio + timedelta(hours=1), 1
            )

    def test_servicio_inactivo_no_reservable(self):
        sala = self.sistema.crear_servicio_sala("S01", "Sala principal")
        sala.desactivar()
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva(
                "R01", "1001", "S01", self.inicio, 1, {"personas": 1}
            )

    def test_monto_no_acepta_nan_o_infinito(self):
        for valor in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(valor=valor):
                with patch("builtins.input", return_value=valor):
                    with self.assertRaises(ValueError):
                        leer_numero("Número: ")

    def test_resumen_inicial(self):
        r = self.sistema.resumen()
        self.assertEqual(r["clientes"], 1)
        self.assertEqual(r["servicios"], 0)
        self.assertEqual(r["reservas"], 0)
        self.assertEqual(r["total_procesado"], 0)
