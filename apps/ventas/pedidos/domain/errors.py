"""Excepciones de dominio del modulo de pedidos.

Heredan de ValueError para mantener compatibilidad con la capa de presentacion,
que traduce estos errores de negocio a respuestas HTTP 400/404.
"""


class PedidoError(ValueError):
    """Error base del dominio de pedidos."""


class CarritoNoEncontrado(PedidoError):
    def __init__(self) -> None:
        super().__init__("Carrito no encontrado")


class CarritoNoPerteneceACliente(PedidoError):
    def __init__(self) -> None:
        super().__init__("El carrito no pertenece al cliente")


class PedidoSinDetalles(PedidoError):
    def __init__(self) -> None:
        super().__init__("Un pedido debe tener al menos un detalle")


class PedidoNoEncontrado(PedidoError):
    def __init__(self) -> None:
        super().__init__("Pedido no encontrado")


class PedidoNoCancelable(PedidoError):
    def __init__(self) -> None:
        super().__init__("No se puede cancelar un pedido pagado")


class PedidoYaPagado(PedidoError):
    def __init__(self) -> None:
        super().__init__("El pedido ya esta pagado")


class PedidoCancelado(PedidoError):
    def __init__(self) -> None:
        super().__init__("No se puede pagar un pedido cancelado")
