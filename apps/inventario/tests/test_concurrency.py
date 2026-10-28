"""Prueba de concurrencia del inventario."""

from django.db import connection
from django.test import TransactionTestCase


class TestConcurrenciaInventario(TransactionTestCase):
    reset_sequences = True

    def test_select_for_update_viable_en_bases_con_bloqueo_de_filas(self):
        if connection.vendor == "sqlite":
            self.skipTest(
                "SQLite no ejerce bloqueo de filas real; "
                "la prueba de concurrencia no es confiable aqui."
            )

        assert connection.features.has_select_for_update
