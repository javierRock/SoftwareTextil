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
    password: str | None = None
    username: str | None = None


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


@dataclass(frozen=True)
class CrearCarritoDTO:
    cliente_id: str


@dataclass(frozen=True)
class AgregarItemCarritoDTO:
    carrito_id: str
    prenda_id: str
    cantidad: int
    precio_unitario: Decimal
    moneda: str = "PEN"


@dataclass(frozen=True)
class ActualizarItemCarritoDTO:
    carrito_id: str
    prenda_id: str
    cantidad: int


@dataclass(frozen=True)
class CrearPedidoDTO:
    carrito_id: str
    cliente_id: str


@dataclass(frozen=True)
class ProcesarPagoDTO:
    pedido_id: str
    monto: Decimal
    metodo: str
    referencia: str = ""
    moneda: str = "PEN"
