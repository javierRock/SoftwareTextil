# SDGT-121 — HF 6.3: Actualizar stock tras confirmar ingreso o salida

## 1. Objetivo
Mantener el saldo de stock y el movimiento de inventario sincronizados y atómicos al confirmar un ingreso o una salida.

## 2. Estado inicial
La base ya estaba implementada en `apps/inventario/application/services.py`: ingreso/salida usan `transaction.atomic()`, `select_for_update()` y guardan stock + movimiento en la misma transacción. También existían pruebas de rollback y stock negativo. Durante la auditoría se corrigió la reconciliación de alertas para que el estado bajo mínimo no quede desactualizado después de recuperar stock.

## 3. Subtareas

| Subtarea | Descripción | Estado | Evidencia |
| -------- | ----------- | ------ | --------- |
| SDGT-122 | Actualizar automáticamente el saldo al confirmar una transacción | Completa | `ServicioInventario.registrar_ingreso()` / `registrar_salida()` |
| SDGT-123 | Validar el cambio del stock después de un ingreso o egreso | Completa | `test_service.py`, `test_api.py`, `test_stock_por_categoria.py` |

## 4. Componentes involucrados

| Archivo o componente | Responsabilidad |
| -------------------- | --------------- |
| `apps/inventario/domain/stock_prenda.py` | Reglas del agregado `StockPrenda` |
| `apps/inventario/application/services.py` | Orquestación transaccional del stock |
| `apps/inventario/infrastructure/repositories.py` | Persistencia ORM y bloqueo de filas |
| `apps/inventario/presentation/views.py` | Exposición de los endpoints de stock |
| `apps/inventario/tests/*` | Cobertura de ingreso, salida, rollback y consistencia |

## 5. Implementación
Flujo real: `POST /api/stock/ingresos/` o `POST /api/stock/salidas/` → serializer → `ServicioInventario` → `select_for_update()` → dominio valida cantidad → repositorio guarda stock → repositorio guarda movimiento → reconciliación de alerta si aplica → respuesta HTTP. El saldo se modifica una sola vez y la operación se revierte si falla el guardado posterior.

## 6. Conflictos y compatibilidad
- Se reutilizó el contrato y la ruta existentes; no se duplicó lógica de inventario.
- `GET /api/stock/por-categoria/` refleja el saldo final sin cambios de contrato.
- **Corrección de dependencia detectada durante SDGT-62:** la reconciliación de alertas se ejecuta con el mismo stock confirmado para no dejar alertas pendientes obsoletas.
- No se cambió `apps/inventario/index.html`.

## 7. Estilos de programación

| Estilo | Estado | Evidencia | Justificación |
| ------ | ------ | --------- | ------------- |
| Things | Verificado | `apps/inventario/domain/stock_prenda.py` | El agregado encapsula ingreso/salida y mantiene invariantes. |
| Pipeline | Verificado | `apps/inventario/presentation/views.py` | La petición sigue una cadena clara: serializer → servicio → repositorio. |
| Error/Exception Handling | Verificado | `apps/inventario/domain/excepciones.py` | Las reglas de stock fallan con excepciones explícitas. |
| Persistent-Tables | Verificado | `apps/inventario/models.py` | Stock, movimientos y alertas viven en tablas separadas. |
| RESTful | Verificado | `apps/inventario/presentation/urls.py` | Los casos de uso se exponen como recursos y acciones HTTP. |
| Lazy-Rivers | No aplicable | N/A | No hay flujos perezosos en esta historia. |
| Trinity | No aplicable | N/A | No se modeló la tríada de capas como patrón independiente. |

**Things**
```python
def registrar_ingreso(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
    self._validar_cantidad(cantidad)
    self.cantidad_actual += cantidad
    self.ultima_actualizacion = datetime.utcnow()
    return self._crear_movimiento(TipoMovimiento.INGRESO, cantidad, motivo, usuario_id)
```
Ruta: `apps/inventario/domain/stock_prenda.py`

**Pipeline**
```python
serializer = MovimientoStockSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
movimiento = servicio.registrar_salida(
    prenda_id=serializer.validated_data["prenda_id"],
    cantidad=serializer.validated_data["cantidad"],
    motivo=serializer.validated_data["motivo"],
    usuario_id=_usuario_responsable_desde_solicitud(request),
)
```
Ruta: `apps/inventario/presentation/views.py`

**Error/Exception Handling**
```python
class StockInsuficiente(ErrorInventario):
    """El stock disponible no alcanza para la operación solicitada."""


def _manejar_error(exc: Exception) -> tuple[dict[str, str], int]:
    if isinstance(exc, (CantidadInvalida, StockInsuficiente, UsuarioResponsableRequerido)):
        return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST
```
Ruta: `apps/inventario/domain/excepciones.py`, `apps/inventario/presentation/views.py`

**Persistent-Tables**
```python
class MovimientoInventarioModel(models.Model):
    stock = models.ForeignKey(StockPrendaModel, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=30)
    cantidad = models.IntegerField()
    motivo = models.TextField()
    registrado_por = models.CharField(max_length=36)
```
Ruta: `apps/inventario/models.py`

**RESTful**
```python
router = DefaultRouter()
router.register(r"stock", StockViewSet, basename="stock")
router.register(r"movimientos", MovimientoViewSet, basename="movimientos")
```
Ruta: `apps/inventario/presentation/urls.py`

## 8. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
| --------- | -------- | --------- |
| Nombres | `StockYaExiste`, `StockInsuficiente`, `registrar_salida` | `apps/inventario/domain/excepciones.py`, `apps/inventario/domain/stock_prenda.py` |
| Funciones | `registrar_ingreso()` y `registrar_salida()` con una sola responsabilidad | `apps/inventario/application/services.py` |
| Estructura | Helpers arriba, endpoints abajo | `apps/inventario/presentation/views.py` |
| Manejo de errores | Excepciones de dominio traducidas a HTTP | `apps/inventario/presentation/views.py` |
| Separación de responsabilidades | Dominio, aplicación, infraestructura y presentación | `apps/inventario/*` |
| Ausencia de duplicación | Se reutiliza el mismo servicio para ingreso y egreso | `apps/inventario/application/services.py` |

## 9. Arquitectura y decisiones
- Capa de dominio: `StockPrenda` mantiene invariantes.
- Capa de aplicación: `ServicioInventario` orquesta transacciones.
- Infraestructura: repositorios Django ORM persisten stock y movimientos.
- Concurrencia: `select_for_update()` protege saldos en actualizaciones concurrentes.
- Permisos: las vistas mantienen `IsAuthenticated`.
- Rendimiento: la consulta agrupada se valida con pruebas de N+1.

## 10. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
| ---- | -------- | ---------- | ------ |
| Dependencia | Alertas potencialmente obsoletas tras recuperar stock | Reconciliación de alertas en el mismo flujo transaccional | Corregido |

## 11. Análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
| ----------- | ------- | -------- | ---------- |
| Revisión manual | No verificado | Ninguno nuevo en esta historia | N/A |
| LSP | No verificado | LSP no disponible en el entorno | N/A |

## 12. Pruebas

| Prueba | Comportamiento | Resultado |
| ------ | -------------- | --------- |
| `test_service.py` | Ingreso/salida, rollback, alerta y duplicados | Pasó |
| `test_api.py` | Endpoint de stock y validaciones HTTP | Pasó |
| `test_stock_por_categoria.py` | Consulta resultante tras operaciones | Pasó |
| `test_concurrency.py` | Bloqueo de filas en bases con soporte | 1 omitida en SQLite |

## 13. Comandos ejecutados

| Comando | Resultado real |
| ------- | -------------- |
| `uv run python manage.py check` | OK |
| `uv run python manage.py makemigrations --check` | OK |
| `uv run pytest apps/inventario -v` | `55 passed, 1 skipped` |

## 14. Archivos creados y modificados
- `apps/inventario/application/services.py`
- `apps/inventario/application/reportes.py`
- `apps/inventario/domain/consultas.py`
- `apps/inventario/domain/repositorios.py`
- `apps/inventario/infrastructure/repositories.py`
- `apps/inventario/presentation/serializers.py`
- `apps/inventario/presentation/views.py`
- `apps/inventario/tests/test_service.py`
- `apps/inventario/tests/test_alertas_api.py`
- `apps/inventario/tests/test_reportes_api.py`
- `docs/historias/SDGT-121-actualizacion-stock.md`

## 15. Limitaciones y deuda técnica
- La prueba de concurrencia real sigue limitada por SQLite.
- El LSP no está instalado, así que no hubo diagnósticos del editor.

## 16. Conclusión
Historia completa en backend y pruebas.
