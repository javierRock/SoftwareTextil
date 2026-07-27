"""Excepciones del dominio de pagos."""


class ErrorPago(Exception):  # noqa: N818 - nombre del lenguaje ubicuo del proyecto
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


class EstadoPagoInvalido(ErrorPago):
    """Indica que el estado no pertenece al ciclo de vida del pago."""

    codigo = "estado_pago_invalido"

    def __init__(self) -> None:
        super().__init__("El estado del pago no es valido.")


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


class LongitudDatoPagoInvalida(ErrorPago):
    """Indica que un dato excede el limite persistible."""

    codigo = "longitud_dato_pago_invalida"

    def __init__(self, campo: str, longitud_maxima: int) -> None:
        super().__init__(
            f"El campo '{campo}' admite como maximo {longitud_maxima} caracteres."
        )


class PedidoNoEncontrado(ErrorPago):
    """Indica que el pedido asociado al pago no existe."""

    codigo = "pedido_no_encontrado"

    def __init__(self, pedido_id: str) -> None:
        super().__init__(f"No se encontro el pedido '{pedido_id}'.")


class PedidoNoPerteneceCliente(ErrorPago):
    """Impide operar sobre el pedido de otro cliente."""

    codigo = "pedido_no_pertenece_cliente"

    def __init__(self) -> None:
        super().__init__("El pedido no pertenece al cliente autenticado.")


class PedidoNoAdmitePago(ErrorPago):
    """Indica que el estado del pedido impide procesar un pago."""

    codigo = "pedido_no_admite_pago"

    def __init__(self) -> None:
        super().__init__("Solo se puede pagar un pedido en estado creado.")


class MontoNoCoincideConPedido(ErrorPago):
    """Exige que el pago unico cubra el total del pedido."""

    codigo = "monto_no_coincide_con_pedido"

    def __init__(self) -> None:
        super().__init__("El monto debe coincidir con el total del pedido.")


class PagoPedidoDuplicado(ErrorPago):
    """Impide registrar mas de un pago para un mismo pedido."""

    codigo = "pago_pedido_duplicado"

    def __init__(self) -> None:
        super().__init__("El pedido ya tiene un pago registrado.")
