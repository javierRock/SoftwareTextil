"""Errores de negocio del contexto de despachos."""

from apps.compartido.domain.errors import DominioError


class DespachoConfirmadoError(DominioError):
    """Un despacho confirmado no vuelve a un estado anterior."""

    def __init__(self) -> None:
        super().__init__("El despacho ya fue confirmado")


class DespachoCanceladoError(DominioError):
    def __init__(self) -> None:
        super().__init__("El despacho esta cancelado")


class DespachoNoPreparadoError(DominioError):
    """No se confirma un despacho que aun no fue preparado."""

    def __init__(self) -> None:
        super().__init__("El despacho debe prepararse antes de confirmarse")


class DireccionDespachoInvalidaError(DominioError):
    def __init__(self) -> None:
        super().__init__("La direccion de entrega no es valida")


class GuiaRemisionInvalidaError(DominioError):
    def __init__(self) -> None:
        super().__init__("La guia de remision no es valida")


class DespachoNoEncontradoError(DominioError):
    def __init__(self) -> None:
        super().__init__("Despacho no encontrado")


class PedidoDespachoNoEncontradoError(DominioError):
    def __init__(self) -> None:
        super().__init__("Pedido no encontrado")


class PedidoNoPagadoError(DominioError):
    def __init__(self) -> None:
        super().__init__("Solo se puede despachar un pedido pagado")


class DespachoYaExisteError(DominioError):
    def __init__(self) -> None:
        super().__init__("El pedido ya tiene un despacho")


class GuiaRemisionDuplicadaError(DominioError):
    def __init__(self) -> None:
        super().__init__("La serie y numero de la guia ya existen")
