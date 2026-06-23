"""DTOs de entrada para casos de uso de aplicacion."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RegistrarPrendaDTO:
    nombre: str
    descripcion: str
    precio: Decimal
    categoria_id: str
    registrado_por: str
    moneda: str = "PEN"
    tipo_producto_id: str | None = None


@dataclass(frozen=True)
class CrearStockDTO:
    prenda_id: str
    stock_inicial: int
    stock_minimo: int
    ubicacion: str = "almacen"


@dataclass(frozen=True)
class MovimientoStockDTO:
    prenda_id: str
    cantidad: int
    motivo: str
    usuario_id: str


@dataclass(frozen=True)
class AjustarStockDTO:
    prenda_id: str
    nueva_cantidad: int
    motivo: str
    usuario_id: str


@dataclass(frozen=True)
class CrearUsuarioDTO:
    nombre: str
    email: str
    rol_id: str
    creado_por: str | None = None


@dataclass(frozen=True)
class LoginDTO:
    username: str
    password: str
    ip: str


@dataclass(frozen=True)
class RegistrarIngresoDTO:
    monto: Decimal
    concepto: str
    moneda: str = "PEN"


@dataclass(frozen=True)
class RegistrarEgresoDTO:
    ruc_proveedor: str
    razon_social: str
    monto: Decimal
    tipo_material: str
    factura: str
    contacto: str = ""
    moneda: str = "PEN"


@dataclass(frozen=True)
class EmitirComprobanteDTO:
    serie: str
    numero: str
    tipo: str
    monto: Decimal
    igv: Decimal
    moneda: str = "PEN"
