"""Composicion de dependencias del monolito modular."""

from software_textil.application.services.servicio_autenticacion import ServicioAutenticacion
from software_textil.application.services.servicio_catalogo import ServicioCatalogo
from software_textil.application.services.servicio_configuracion import ServicioConfiguracion
from software_textil.application.services.servicio_contabilidad import ServicioContabilidad
from software_textil.application.services.servicio_despachos import ServicioDespachos
from software_textil.application.services.servicio_facturacion import ServicioFacturacion
from software_textil.application.services.servicio_gestion_usuarios import ServicioGestionUsuarios
from software_textil.application.services.servicio_inventario import ServicioInventario
from software_textil.application.services.servicio_reportes import ServicioReportes
from software_textil.domain.configuracion.configuracion import ConfiguracionFabrica
from software_textil.infrastructure.external_services.sunat_client import SunatClient
from software_textil.infrastructure.repositories.in_memory import (
    InMemoryAlertaStockRepository,
    InMemoryCatalogoRepository,
    InMemoryConfiguracionRepository,
    InMemoryDespachoRepository,
    InMemoryEgresoRepository,
    InMemoryIngresoRepository,
    InMemoryIntentoLoginRepository,
    InMemoryInventarioRepository,
    InMemoryMovimientoRepository,
    InMemoryPeriodoContableRepository,
    InMemoryPrendaRepository,
    InMemoryReporteRepository,
    InMemoryRolRepository,
    InMemorySesionRepository,
    InMemoryUsuarioRepository,
)


def crear_servicios() -> dict[str, object]:
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

    return {
        "catalogo": ServicioCatalogo(prendas, catalogo),
        "inventario": ServicioInventario(inventario, movimientos, alertas),
        "usuarios": ServicioGestionUsuarios(usuarios, roles),
        "autenticacion": ServicioAutenticacion(usuarios, sesiones, intentos),
        "reportes": ServicioReportes(reportes),
        "contabilidad": ServicioContabilidad(ingresos, egresos, periodos),
        "facturacion": ServicioFacturacion(SunatClient()),
        "configuracion": ServicioConfiguracion(configuraciones),
        "despachos": ServicioDespachos(despachos),
    }
