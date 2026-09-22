# Evidencia SOLID y correcciones del módulo de inventario

## Alcance

Este documento resume la implementación backend realizada para las 3 historias más representativas:

- SDGT-121 — Actualizar stock tras confirmar ingreso o salida.
- SDGT-62 — Recibir alertas de stock bajo.
- SDGT-67 — Generar reporte del inventario actual.

> SDGT-124 queda fuera de este resumen porque está bloqueada por ausencia de modelos reales de despacho/cliente/dirección.

## 1. Principios SOLID aplicados

### 1.1 SRP — Single Responsibility Principle

**Aplicación:** la vista solo traduce HTTP y el servicio orquesta el caso de uso.

**Fragmento de código:**

```python
# apps/inventario/presentation/views.py
class StockViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="reporte")
    def reporte(self, request):
        serializer = ReporteInventarioQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio_reporte()
        archivo = servicio.generar_archivo(
            formato=serializer.validated_data["formato"],
            categoria_id=serializer.validated_data.get("categoria_id") or None,
        )
        respuesta = HttpResponse(archivo.contenido, content_type=archivo.content_type)
        return respuesta
```

**Por qué aplica:** la vista no calcula stock, no arma reportes y no decide reglas de negocio.

### 1.2 DIP — Dependency Inversion Principle

**Aplicación:** el servicio depende de contratos del dominio, no de repositorios Django concretos.

**Fragmento de código:**

```python
# apps/inventario/application/services.py
class ServicioInventario:
    def __init__(
        self,
        repo_inventario: RepositorioInventario,
        repo_movimientos: RepositorioMovimientoInventario,
        repo_alertas: RepositorioAlertaStock,
        repo_prenda: RepositorioPrenda | None = None,
        repo_catalogo: RepositorioCatalogo | None = None,
    ) -> None:
        self.repo_inventario = repo_inventario
        self.repo_movimientos = repo_movimientos
        self.repo_alertas = repo_alertas
```

**Por qué aplica:** el caso de uso puede probarse con dobles sin tocar ORM ni views.

### 1.3 LSP — Liskov Substitution Principle

**Aplicación:** el repositorio concreto sustituye al contrato abstracto sin cambiar el comportamiento esperado.

**Fragmento de código:**

```python
# apps/inventario/infrastructure/repositories.py
class DjangoRepositorioInventario(RepositorioInventario):
    def guardar(self, stock: StockPrenda) -> None:
        model = StockPrendaModel.objects.filter(id=stock.id).first()
        if model is None:
            model = StockPrendaModel(id=stock.id)
        model.prenda_id = stock.prenda_id
        model.cantidad_actual = stock.cantidad_actual
        model.nivel_minimo = stock.nivel_minimo
        model.ubicacion = stock.ubicacion
        model.unidad = stock.unidad
        model.save()
```

**Por qué aplica:** `ServicioInventario` puede recibir este adaptador sin conocer detalles de persistencia.

### 1.4 ISP — Interface Segregation Principle

**Aplicación:** cada contrato expone solo lo necesario para su caso de uso.

**Fragmento de código:**

```python
# apps/inventario/domain/repositorios.py
class RepositorioMovimientoInventario(ABC):
    @abstractmethod
    def guardar(self, movimiento: MovimientoInventario) -> None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_stock(self, stock_id: str) -> list[MovimientoInventario]:
        raise NotImplementedError


class RepositorioAlertaStock(ABC):
    @abstractmethod
    def guardar(self, alerta: AlertaStock) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_pendiente_por_stock(self, stock_id: str) -> AlertaStock | None:
        raise NotImplementedError
```

**Por qué aplica:** evita interfaces gigantes y mantiene el dominio fácil de probar.

## 2. Bugs, code smells y vulnerabilidades corregidos

| Tipo | Error encontrado | Solución aplicada | Estado |
| ---- | ---------------- | ----------------- | ------ |
| Bug | La exportación XLSX dependía de `openpyxl`, pero el entorno no lo tenía instalado. | Se generó el XLSX con `zipfile` + XML estándar de Office. | Corregido |
| Bug de dominio | Las alertas bajo mínimo podían quedarse obsoletas si el stock se recuperaba y luego volvía a bajar. | Se marca la alerta como atendida al recuperarse el stock y se crea una nueva si cruza otra vez el umbral. | Corregido |
| Code smell | La documentación y las rutas de historias quedaron duplicadas durante la reorganización. | Se normalizó la ubicación final y se dejó `docs/historias/README.md` apuntando a `docs/guias/inventario/`. | Corregido |
| Vulnerabilidad | No se debe confiar en datos del cliente para decidir el responsable de un movimiento. | La vista usa `request.user.id` como fuente de verdad. | Corregido |

## 3. Principio + fragmento de código

| Principio | Fragmento |
| --------- | --------- |
| SRP | `StockViewSet.reporte()` solo recibe, valida y responde. |
| DIP | `ServicioInventario` depende de `RepositorioInventario`, `RepositorioMovimientoInventario` y `RepositorioAlertaStock`. |
| LSP | `DjangoRepositorioInventario(RepositorioInventario)` sustituye al contrato sin romper al servicio. |
| ISP | `RepositorioMovimientoInventario` y `RepositorioAlertaStock` tienen contratos pequeños y específicos. |

## 4. Conclusión

La implementación del módulo de inventario usa separación clara de responsabilidades, inversión de dependencias y contratos pequeños. Además, las correcciones reales de esta entrega eliminaron una dependencia rota de exportación, un comportamiento inconsistente de alertas y un punto de confianza indebida en la entrada del cliente.
