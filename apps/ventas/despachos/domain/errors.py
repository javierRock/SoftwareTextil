"""Errores de negocio del contexto de despachos."""

from apps.compartido.domain.errors import DominioError


class DespachoConfirmadoError(DominioError):
    """Un despacho confirmado no vuelve a un estado anterior."""

    def __init__(self) -> None:
        super().__init__("El despacho ya fue confirmado")


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
