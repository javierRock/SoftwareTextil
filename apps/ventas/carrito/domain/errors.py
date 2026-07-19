"""Excepciones de dominio del modulo de carrito.

Heredan de ValueError para mantener compatibilidad con la capa de presentacion,
que traduce estos errores de negocio a respuestas HTTP 400/404.
"""


class CarritoError(ValueError):
    """Error base del dominio de carrito."""


class CarritoNoEncontrado(CarritoError):
    def __init__(self) -> None:
        super().__init__("Carrito no encontrado")


class CarritoCerrado(CarritoError):
    def __init__(self) -> None:
        super().__init__("El carrito no esta abierto")


class CantidadInvalida(CarritoError):
    def __init__(self) -> None:
        super().__init__("La cantidad del item debe ser mayor a cero")


class MonedasIncompatibles(CarritoError):
    def __init__(self) -> None:
        super().__init__("No se pueden mezclar monedas en el carrito")


class ItemInexistente(CarritoError):
    def __init__(self) -> None:
        super().__init__("El item no existe en el carrito")


class CarritoVacio(CarritoError):
    def __init__(self) -> None:
        super().__init__("No se puede generar un pedido desde un carrito vacio")


class CarritoConvertido(CarritoError):
    def __init__(self) -> None:
        super().__init__("No se puede cancelar un carrito convertido")
