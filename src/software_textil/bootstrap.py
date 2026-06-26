"""Composicion de dependencias del monolito modular."""

from software_textil.application.services.servicio_autenticacion import ServicioAutenticacion
from software_textil.application.services.servicio_catalogo import ServicioCatalogo
from software_textil.application.services.servicio_compras import ServicioCompras
from software_textil.application.services.servicio_configuracion import ServicioConfiguracion
from software_textil.application.services.servicio_contabilidad import ServicioContabilidad
from software_textil.application.services.servicio_despachos import ServicioDespachos
from software_textil.application.services.servicio_facturacion import ServicioFacturacion
from software_textil.application.services.servicio_gestion_usuarios import ServicioGestionUsuarios
from software_textil.application.services.servicio_inventario import ServicioInventario
from software_textil.application.services.servicio_pagos import ServicioPagos
from software_textil.application.services.servicio_pedidos import ServicioPedidos
from software_textil.application.services.servicio_reportes import ServicioReportes
from software_textil.domain.configuracion.configuracion import ConfiguracionFabrica
from software_textil.infrastructure.external_services.sunat_client import SunatClient
from software_textil.infrastructure.repositories.in_memory import (
    InMemoryAlertaStockRepository,
    InMemoryCarritoRepository,
    InMemoryCatalogoRepository,
    InMemoryConfiguracionRepository,
    InMemoryDespachoRepository,
    InMemoryEgresoRepository,
    InMemoryIngresoRepository,
    InMemoryIntentoLoginRepository,
    InMemoryInventarioRepository,
    InMemoryMovimientoRepository,
    InMemoryPagoRepository,
    InMemoryPedidoRepository,
    InMemoryPeriodoContableRepository,
    InMemoryPrendaRepository,
    InMemoryReporteRepository,
    InMemoryRolRepository,
    InMemorySesionRepository,
    InMemoryUsuarioRepository,
)
from software_textil.infrastructure.repositories.sqlalchemy_compras_repository import SQLAlchemyCarritoRepository
from software_textil.infrastructure.repositories.sqlalchemy_pagos_repository import SQLAlchemyPagoRepository
from software_textil.infrastructure.repositories.sqlalchemy_pedidos_repository import SQLAlchemyPedidoRepository
from software_textil.infrastructure.security import WorkzeugPasswordHasher
from software_textil.infrastructure.unit_of_work import InMemoryUnitOfWork, SQLAlchemyUnitOfWork


def crear_servicios(persistence_backend: str = "memory") -> dict[str, object]:
    if persistence_backend not in {"memory", "sqlalchemy"}:
        raise ValueError("Backend de persistencia no soportado")

    password_hasher = WorkzeugPasswordHasher()
    memory_uow = InMemoryUnitOfWork()
    checkout_uow = SQLAlchemyUnitOfWork() if persistence_backend == "sqlalchemy" else memory_uow
    prendas = InMemoryPrendaRepository()
    catalogo = InMemoryCatalogoRepository()
    inventario = InMemoryInventarioRepository()
    movimientos = InMemoryMovimientoRepository()
    alertas = InMemoryAlertaStockRepository()
    usuarios = InMemoryUsuarioRepository()
    roles = InMemoryRolRepository()
    sesiones = InMemorySesionRepository()
    intentos = InMemoryIntentoLoginRepository()
    reportes = InMemoryReporteRepository()
    ingresos = InMemoryIngresoRepository()
    egresos = InMemoryEgresoRepository()
    periodos = InMemoryPeriodoContableRepository()
    configuraciones = InMemoryConfiguracionRepository(ConfiguracionFabrica.crear_default())
    despachos = InMemoryDespachoRepository()

    if persistence_backend == "sqlalchemy":
        carritos = SQLAlchemyCarritoRepository()
        pedidos = SQLAlchemyPedidoRepository()
        pagos = SQLAlchemyPagoRepository()
    else:
        carritos = InMemoryCarritoRepository()
        pedidos = InMemoryPedidoRepository()
        pagos = InMemoryPagoRepository()

    return {
        "catalogo": ServicioCatalogo(prendas, catalogo, memory_uow),
        "inventario": ServicioInventario(inventario, movimientos, alertas, memory_uow),
        "usuarios": ServicioGestionUsuarios(usuarios, roles, password_hasher, memory_uow),
        "autenticacion": ServicioAutenticacion(usuarios, sesiones, intentos, password_hasher, memory_uow),
        "reportes": ServicioReportes(reportes, memory_uow),
        "contabilidad": ServicioContabilidad(ingresos, egresos, periodos, memory_uow),
        "facturacion": ServicioFacturacion(SunatClient()),
        "configuracion": ServicioConfiguracion(configuraciones, memory_uow),
        "despachos": ServicioDespachos(despachos, memory_uow),
        "compras": ServicioCompras(carritos, checkout_uow),
        "pedidos": ServicioPedidos(pedidos, carritos, checkout_uow),
        "pagos": ServicioPagos(pagos, pedidos, checkout_uow),
        "unit_of_work": checkout_uow,
        "persistence_backend": persistence_backend,
    }
