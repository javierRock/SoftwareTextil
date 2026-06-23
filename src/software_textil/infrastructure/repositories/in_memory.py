"""Repositorios en memoria para pruebas, prototipos y controladores iniciales."""

from datetime import datetime

from software_textil.domain.auditoria.registro_auditoria import RegistroAuditoria
from software_textil.domain.auditoria.repositorios import RepositorioAuditoria
from software_textil.domain.catalogo.prenda import Categoria, Prenda, TipoProducto
from software_textil.domain.catalogo.repositorios import RepositorioCatalogo, RepositorioPrenda
from software_textil.domain.configuracion.configuracion import ConfiguracionGeneral
from software_textil.domain.configuracion.repositorios import RepositorioConfiguracion
from software_textil.domain.contabilidad.contabilidad import EgresoTextil, Ingreso, PeriodoContable
from software_textil.domain.contabilidad.repositorios import RepositorioEgreso, RepositorioIngreso, RepositorioPeriodoContable
from software_textil.domain.despachos.despacho import Despacho
from software_textil.domain.despachos.repositorios import RepositorioDespacho
from software_textil.domain.inventario.repositorios import RepositorioAlertaStock, RepositorioInventario, RepositorioMovimientoInventario
from software_textil.domain.inventario.stock_prenda import AlertaStock, MovimientoInventario, StockPrenda
from software_textil.domain.reportes.reporte import Reporte
from software_textil.domain.reportes.repositorios import RepositorioReporte
from software_textil.domain.usuarios.repositorios import RepositorioIntentoLogin, RepositorioRol, RepositorioSesion, RepositorioUsuario
from software_textil.domain.usuarios.usuario import IntentoLogin, Rol, Sesion, Usuario


class InMemoryPrendaRepository(RepositorioPrenda):
    def __init__(self) -> None:
        self.items: dict[str, Prenda] = {}

    def guardar(self, prenda: Prenda) -> None:
        self.items[prenda.id] = prenda

    def buscar_por_id(self, prenda_id: str) -> Prenda | None:
        return self.items.get(prenda_id)

    def listar(self) -> list[Prenda]:
        return list(self.items.values())


class InMemoryCatalogoRepository(RepositorioCatalogo):
    def __init__(self) -> None:
        self.categorias: dict[str, Categoria] = {}
        self.tipos_producto: dict[str, TipoProducto] = {}

    def guardar_categoria(self, categoria: Categoria) -> None:
        self.categorias[categoria.id] = categoria

    def guardar_tipo_producto(self, tipo_producto: TipoProducto) -> None:
        self.tipos_producto[tipo_producto.id] = tipo_producto


class InMemoryInventarioRepository(RepositorioInventario):
    def __init__(self) -> None:
        self.items: dict[str, StockPrenda] = {}

    def guardar(self, stock: StockPrenda) -> None:
        self.items[stock.id] = stock

    def buscar_por_prenda(self, prenda_id: str) -> StockPrenda | None:
        return next((stock for stock in self.items.values() if stock.prenda_id == prenda_id), None)

    def buscar_por_id(self, stock_id: str) -> StockPrenda | None:
        return self.items.get(stock_id)


class InMemoryMovimientoRepository(RepositorioMovimientoInventario):
    def __init__(self) -> None:
        self.items: dict[str, MovimientoInventario] = {}

    def guardar(self, movimiento: MovimientoInventario) -> None:
        self.items[movimiento.id] = movimiento

    def listar_por_stock(self, stock_id: str) -> list[MovimientoInventario]:
        return [movimiento for movimiento in self.items.values() if movimiento.stock_id == stock_id]


class InMemoryAlertaStockRepository(RepositorioAlertaStock):
    def __init__(self) -> None:
        self.items: dict[str, AlertaStock] = {}

    def guardar(self, alerta: AlertaStock) -> None:
        self.items[alerta.id] = alerta


class InMemoryUsuarioRepository(RepositorioUsuario):
    def __init__(self) -> None:
        self.items: dict[str, Usuario] = {}

    def guardar(self, usuario: Usuario) -> None:
        self.items[usuario.id] = usuario

    def buscar_por_id(self, usuario_id: str) -> Usuario | None:
        return self.items.get(usuario_id)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return next((usuario for usuario in self.items.values() if usuario.email == email), None)


class InMemoryRolRepository(RepositorioRol):
    def __init__(self) -> None:
        self.items: dict[str, Rol] = {}

    def guardar(self, rol: Rol) -> None:
        self.items[rol.id] = rol

    def buscar_por_id(self, rol_id: str) -> Rol | None:
        return self.items.get(rol_id)


class InMemorySesionRepository(RepositorioSesion):
    def __init__(self) -> None:
        self.items: dict[str, Sesion] = {}

    def guardar(self, sesion: Sesion) -> None:
        self.items[sesion.token] = sesion

    def buscar_por_token(self, token: str) -> Sesion | None:
        return self.items.get(token)


class InMemoryIntentoLoginRepository(RepositorioIntentoLogin):
    def __init__(self) -> None:
        self.items: list[IntentoLogin] = []

    def guardar(self, intento: IntentoLogin) -> None:
        self.items.append(intento)


class InMemoryReporteRepository(RepositorioReporte):
    def __init__(self) -> None:
        self.items: dict[str, Reporte] = {}

    def guardar(self, reporte: Reporte) -> None:
        self.items[reporte.id] = reporte

    def buscar_por_id(self, reporte_id: str) -> Reporte | None:
        return self.items.get(reporte_id)


class InMemoryIngresoRepository(RepositorioIngreso):
    def __init__(self) -> None:
        self.items: dict[str, Ingreso] = {}

    def guardar(self, ingreso: Ingreso) -> None:
        self.items[ingreso.id] = ingreso

    def listar_por_fecha(self, desde: datetime, hasta: datetime) -> list[Ingreso]:
        return [ingreso for ingreso in self.items.values() if desde <= ingreso.fecha <= hasta]


class InMemoryEgresoRepository(RepositorioEgreso):
    def __init__(self) -> None:
        self.items: dict[str, EgresoTextil] = {}

    def guardar(self, egreso: EgresoTextil) -> None:
        self.items[egreso.id] = egreso

    def listar_por_fecha(self, desde: datetime, hasta: datetime) -> list[EgresoTextil]:
        return list(self.items.values())


class InMemoryPeriodoContableRepository(RepositorioPeriodoContable):
    def __init__(self) -> None:
        self.items: list[PeriodoContable] = []

    def guardar(self, periodo: PeriodoContable) -> None:
        self.items.append(periodo)


class InMemoryDespachoRepository(RepositorioDespacho):
    def __init__(self) -> None:
        self.items: dict[str, Despacho] = {}

    def guardar(self, despacho: Despacho) -> None:
        self.items[despacho.id] = despacho

    def buscar_por_id(self, despacho_id: str) -> Despacho | None:
        return self.items.get(despacho_id)


class InMemoryAuditoriaRepository(RepositorioAuditoria):
    def __init__(self) -> None:
        self.items: list[RegistroAuditoria] = []

    def guardar(self, registro: RegistroAuditoria) -> None:
        self.items.append(registro)


class InMemoryConfiguracionRepository(RepositorioConfiguracion):
    def __init__(self, configuracion: ConfiguracionGeneral | None = None) -> None:
        self.configuracion = configuracion

    def guardar(self, configuracion: ConfiguracionGeneral) -> None:
        self.configuracion = configuracion

    def obtener(self) -> ConfiguracionGeneral | None:
        return self.configuracion
