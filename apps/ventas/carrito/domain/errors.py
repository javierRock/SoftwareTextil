"""Excepciones de dominio del modulo de carrito.

Cuelgan de `DominioError` para que la capa de presentacion las traduzca a
respuestas HTTP 400/404 sin conocer cada subtipo.
"""

from apps.compartido.domain.errors import DominioError


class CarritoError(DominioError):
    """Error base del dominio de carrito."""


class CarritoNoEncontradoError(CarritoError):
    def __init__(self) -> None:
        super().__init__("Carrito no encontrado")


class CarritoCerradoError(CarritoError):
    def __init__(self) -> None:
        super().__init__("El carrito no esta abierto")


class CantidadInvalidaError(CarritoError):
    def __init__(self) -> None:
        super().__init__("La cantidad del item debe ser mayor a cero")


class MonedasIncompatiblesError(CarritoError):
    def __init__(self) -> None:
        super().__init__("No se pueden mezclar monedas en el carrito")


class ItemInexistenteError(CarritoError):
    def __init__(self) -> None:
        super().__init__("El item no existe en el carrito")


class CarritoVacioError(CarritoError):
    def __init__(self) -> None:
        super().__init__("No se puede generar un pedido desde un carrito vacio")


class CarritoConvertidoError(CarritoError):
    def __init__(self) -> None:
        super().__init__("No se puede cancelar un carrito convertido")
