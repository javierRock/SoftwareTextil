"""Excepciones de dominio para inventario.

Heredan de `DominioError` para que un caso de uso que orqueste varios modulos
pueda capturarlas junto al resto de violaciones de negocio, y para que la tabla
`ESTADOS_HTTP` de la capa de presentacion las traduzca sin casos especiales.
"""

from apps.compartido.domain.errors import DominioError


class InventarioError(DominioError):
    """Base para errores de negocio del inventario."""


class CantidadInvalidaError(InventarioError):
    """La cantidad indicada no cumple las reglas del negocio."""


class VarianteNoEncontradaError(InventarioError):
    """La variante solicitada no existe en el catalogo."""


class StockNoEncontradoError(InventarioError):
    """No existe stock para la variante indicada."""


class StockInsuficienteError(InventarioError):
    """El stock disponible no alcanza para la operacion solicitada."""


class StockYaExisteError(InventarioError):
    """Ya existe un stock registrado para la variante indicada."""


class ReservaInvalidaError(InventarioError):
    """No se puede reservar o liberar la cantidad solicitada."""


class UsuarioResponsableRequeridoError(InventarioError):
    """No fue posible determinar el usuario responsable."""


class CategoriaNoEncontradaError(InventarioError):
    """La categoria solicitada no existe."""
