"""Excepciones de dominio del modulo de pedidos.

Cuelgan de `DominioError` para que la capa de presentacion las traduzca a
respuestas HTTP 400/404 sin conocer cada subtipo.
"""

from apps.compartido.domain.errors import DominioError


class PedidoError(DominioError):
    """Error base del dominio de pedidos."""


class CarritoNoEncontradoError(PedidoError):
    def __init__(self) -> None:
        super().__init__("Carrito no encontrado")


class CarritoNoPerteneceAClienteError(PedidoError):
    def __init__(self) -> None:
        super().__init__("El carrito no pertenece al cliente")


class PedidoSinDetallesError(PedidoError):
    def __init__(self) -> None:
        super().__init__("Un pedido debe tener al menos un detalle")


class CantidadDetalleInvalidaError(PedidoError):
    def __init__(self) -> None:
        super().__init__("La cantidad del detalle debe ser mayor a cero")


class PedidoNoEncontradoError(PedidoError):
    def __init__(self) -> None:
        super().__init__("Pedido no encontrado")


class PedidoNoPerteneceAClienteError(PedidoError):
    def __init__(self) -> None:
        super().__init__("El pedido no pertenece al cliente")


class PedidoNoCancelableError(PedidoError):
    def __init__(self) -> None:
        super().__init__("No se puede cancelar un pedido pagado")


class PedidoYaPagadoError(PedidoError):
    def __init__(self) -> None:
        super().__init__("El pedido ya esta pagado")


class PedidoCanceladoError(PedidoError):
    def __init__(self) -> None:
        super().__init__("No se puede pagar un pedido cancelado")


class PedidoYaCanceladoError(PedidoError):
    def __init__(self) -> None:
        super().__init__("El pedido ya fue cancelado")
