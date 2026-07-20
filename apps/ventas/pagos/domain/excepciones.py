"""Excepciones del dominio de pagos."""


class ErrorPago(Exception):
    """Error base controlado del modulo de pagos."""

    codigo = "error_pago"


class PagoNoEncontrado(ErrorPago):
    """Indica que el pago solicitado no existe."""

    codigo = "pago_no_encontrado"

    def __init__(self, pago_id: str) -> None:
        super().__init__(f"No se encontro el pago '{pago_id}'.")


class PagoYaProcesado(ErrorPago):
    """Impide modificar un pago que alcanzo un estado final."""

    codigo = "pago_ya_procesado"

    def __init__(self) -> None:
        super().__init__("Solo se puede procesar un pago pendiente.")


class MontoPagoInvalido(ErrorPago):
    """Indica que el importe no es estrictamente positivo."""

    codigo = "monto_pago_invalido"

    def __init__(self) -> None:
        super().__init__("El monto del pago debe ser mayor que cero.")


class MetodoPagoNoSoportado(ErrorPago):
    """Indica que el metodo solicitado no pertenece al dominio."""

    codigo = "metodo_pago_no_soportado"

    def __init__(self, metodo: object) -> None:
        super().__init__(f"El metodo de pago '{metodo}' no esta soportado.")


class ReferenciaPagoInvalida(ErrorPago):
    """Indica que falta la referencia requerida por el metodo."""

    codigo = "referencia_pago_invalida"

    def __init__(self, metodo: object) -> None:
        super().__init__(f"El metodo de pago '{metodo}' requiere una referencia.")


class PedidoPagoInvalido(ErrorPago):
    """Indica que no se proporciono un identificador de pedido valido."""

    codigo = "pedido_pago_invalido"

    def __init__(self) -> None:
        super().__init__("El identificador del pedido es obligatorio.")


class IdentificadorPagoInvalido(ErrorPago):
    """Indica que no se proporciono un identificador de pago valido."""

    codigo = "identificador_pago_invalido"

    def __init__(self) -> None:
        super().__init__("El identificador del pago es obligatorio.")
