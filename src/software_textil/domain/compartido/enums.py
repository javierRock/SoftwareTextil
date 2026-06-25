"""Enumeraciones compartidas del dominio textil."""

from enum import StrEnum


class EstadoAlerta(StrEnum):
    PENDIENTE = "pendiente"
    ATENDIDA = "atendida"


class EstadoDespacho(StrEnum):
    PENDIENTE = "pendiente"
    PREPARADO = "preparado"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"


class EstadoCarrito(StrEnum):
    ABIERTO = "abierto"
    CONVERTIDO = "convertido"
    CANCELADO = "cancelado"


class EstadoPedido(StrEnum):
    CREADO = "creado"
    PAGADO = "pagado"
    CANCELADO = "cancelado"


class EstadoPago(StrEnum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class MetodoPago(StrEnum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    YAPE = "yape"


class EstadoPrenda(StrEnum):
    ACTIVA = "activa"
    INACTIVA = "inactiva"


class EstadoSesion(StrEnum):
    ACTIVA = "activa"
    EXPIRADA = "expirada"
    CERRADA = "cerrada"


class EstadoUsuario(StrEnum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"


class FormatoReporte(StrEnum):
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"


class ResultadoLogin(StrEnum):
    EXITOSO = "exitoso"
    CREDENCIALES_INVALIDAS = "credenciales_invalidas"
    USUARIO_INACTIVO = "usuario_inactivo"


class TipoComprobante(StrEnum):
    FACTURA = "factura"
    BOLETA = "boleta"


class TipoMovimiento(StrEnum):
    INGRESO = "ingreso"
    SALIDA = "salida"
    AJUSTE = "ajuste"
