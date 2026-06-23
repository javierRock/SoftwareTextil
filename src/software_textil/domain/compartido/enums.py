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
