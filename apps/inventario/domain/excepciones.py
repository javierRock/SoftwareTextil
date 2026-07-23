"""Excepciones de dominio para inventario."""


class ErrorInventario(Exception):
    """Base para errores de negocio del inventario."""


class CantidadInvalida(ErrorInventario):
    """La cantidad indicada no cumple las reglas del negocio."""


class PrendaNoEncontrada(ErrorInventario):
    """La prenda solicitada no existe."""


class StockNoEncontrado(ErrorInventario):
    """No existe stock para la prenda indicada."""


class StockInsuficiente(ErrorInventario):
    """El stock disponible no alcanza para la operación solicitada."""


class StockYaExiste(ErrorInventario):
    """Ya existe un stock registrado para la prenda indicada."""


class UsuarioResponsableRequerido(ErrorInventario):
    """No fue posible determinar el usuario responsable."""
