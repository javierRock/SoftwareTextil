# SDGT-62 — HF 3.2: Recibir alertas de stock bajo

## 1. Objetivo
Detectar prendas bajo el mínimo configurado por stock, exponerlas por API y mantener alertas coherentes cuando el stock baja, se recupera y vuelve a caer.

## 2. Estado inicial
Existía el campo `nivel_minimo` en `StockPrendaModel`, el método de dominio `esta_bajo_minimo()` y la tabla `alertas_stock`, pero no había endpoint de consumo ni reconciliación completa de estados. La alerta se persistía, pero no se atendía al recuperar stock.

## 3. Subtareas

| Subtarea | Descripción | Estado | Evidencia |
| -------- | ----------- | ------ | --------- |
| SDGT-63 | Interfaz de notificaciones y alertas | Parcial | Backend listo; frontend no modificado por instrucción actual |
| SDGT-64 | Lógica backend para detectar stock inferior al mínimo | Completa | `ServicioInventario.listar_stock_bajo_minimo()` |
| SDGT-65 | Validar la alerta después de una venta | Completa | `test_service.py`, `test_alertas_api.py` |
| SDGT-66 | Evitar alertas duplicadas | Completa | Reconciliación en `ServicioInventario._generar_alerta_si_corresponde()` |

## 4. Componentes involucrados

| Archivo o componente | Responsabilidad |
| -------------------- | --------------- |
| `apps/inventario/domain/stock_prenda.py` | Umbral de stock bajo y creación de alerta |
| `apps/inventario/domain/consultas.py` | DTO de stock bajo mínimo |
| `apps/inventario/application/services.py` | Reconciliación y consulta de alertas |
| `apps/inventario/infrastructure/repositories.py` | Consulta eficiente sin N+1 |
| `apps/inventario/presentation/views.py` | Endpoint `bajo-minimo` |
| `apps/inventario/tests/test_alertas_api.py` | Cobertura HTTP de alertas |

## 5. Implementación
La fuente de verdad sigue siendo el stock. El sistema evalúa `stock < nivel_minimo`, expone `GET /api/stock/bajo-minimo/` y reutiliza la persistencia existente solo como registro de estados. Cuando un stock vuelve a subir por encima del mínimo, la alerta pendiente se marca como atendida; si luego vuelve a cruzar el umbral, se crea una nueva alerta.

## 6. Conflictos y compatibilidad
- Se reutilizó `nivel_minimo` por prenda; no se inventó configuración global.
- Se evitó una segunda fuente de verdad: el endpoint lee stock real, no la tabla de alertas.
- **Corrección de dependencia detectada durante SDGT-62:** la reconciliación de alertas se ajustó junto con las operaciones de stock para no dejar estados inconsistentes.
- No se tocó `apps/inventario/index.html`.

## 7. Estilos de programación

| Estilo | Estado | Evidencia | Justificación |
| ------ | ------ | --------- | ------------- |
| Things | Verificado | `apps/inventario/domain/stock_prenda.py` | El agregado decide cuándo hay alerta. |
| Pipeline | Verificado | `apps/inventario/presentation/views.py` | Serializer → servicio → repositorio → respuesta. |
| Error/Exception Handling | Verificado | `apps/inventario/domain/excepciones.py` | Se diferencian cantidades inválidas y stock insuficiente. |
| Persistent-Tables | Verificado | `apps/inventario/infrastructure/repositories.py` | Consulta y persistencia usan tablas reales con FK. |
| RESTful | Verificado | `apps/inventario/presentation/views.py` | Alertas expuestas como recurso `/api/stock/bajo-minimo/`. |
| Lazy-Rivers | No aplicable | N/A | No hay streams perezosos en esta historia. |
| Trinity | No aplicable | N/A | No se introdujo un patrón nuevo de tres capas adicional. |

**Things**
```python
def esta_bajo_minimo(self) -> bool:
    return self.cantidad_actual < self.nivel_minimo


def generar_alerta_si_corresponde(self) -> AlertaStock | None:
    if not self.esta_bajo_minimo():
        return None
```
Ruta: `apps/inventario/domain/stock_prenda.py`

**Pipeline**
```python
@action(detail=False, methods=["get"], url_path="bajo-minimo")
def bajo_minimo(self, request):
    alertas = _servicio().listar_stock_bajo_minimo()
    return Response(PrendaStockBajoMinimoSerializer(alertas, many=True).data)
```
Ruta: `apps/inventario/presentation/views.py`

**Error/Exception Handling**
```python
class StockInsuficiente(ErrorInventario):
    """El stock disponible no alcanza para la operación solicitada."""
```
Ruta: `apps/inventario/domain/excepciones.py`

**Persistent-Tables**
```python
stocks = list(StockPrendaModel.objects.filter(cantidad_actual__lt=F("nivel_minimo")))
prendas = PrendaModel.objects.select_related("categoria").filter(id__in=[stock.prenda_id for stock in stocks])
```
Ruta: `apps/inventario/infrastructure/repositories.py`

**RESTful**
```python
router = DefaultRouter()
router.register(r"stock", StockViewSet, basename="stock")
```
Ruta: `apps/inventario/presentation/urls.py`

## 8. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
| --------- | -------- | --------- |
| Nombres | `PrendaStockBajoMinimo`, `listar_stock_bajo_minimo` | `apps/inventario/domain/consultas.py`, `apps/inventario/application/services.py` |
| Funciones | Reconcilia alerta sin mezclar HTTP y dominio | `apps/inventario/application/services.py` |
| Estructura | Endpoint separado del CRUD de stock | `apps/inventario/presentation/views.py` |
| Manejo de errores | 404/400 coherentes con el dominio | `apps/inventario/presentation/views.py` |
| Separación de responsabilidades | Consulta de bajo mínimo en repositorio, no en vista | `apps/inventario/infrastructure/repositories.py` |
| Ausencia de duplicación | Se reutiliza el stock real para alertas y reportes | `apps/inventario/application/services.py` |

## 9. Arquitectura y decisiones
- El umbral sigue viviendo en `StockPrendaModel`.
- La baja se evalúa por comparación estricta: `stock < mínimo`.
- La persistencia de alertas es auxiliar; la verdad está en el stock.
- La consulta evita N+1 con dos consultas ORM.
- El acceso está protegido con `IsAuthenticated`.

## 10. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
| ---- | -------- | ---------- | ------ |
| Duplicado lógico | Alertas pendientes no se atendían al recuperar stock | Se marca la alerta como atendida y se vuelve a crear si cruza otra vez | Corregido |

## 11. Análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
| ----------- | ------- | -------- | ---------- |
| Revisión manual | No verificado | Ninguno nuevo en esta historia | N/A |
| LSP | No verificado | LSP no disponible en el entorno | N/A |

## 12. Pruebas

| Prueba | Comportamiento | Resultado |
| ------ | -------------- | --------- |
| `test_alertas_api.py` | Umbral, cero, lista vacía, permisos | Pasó |
| `test_service.py` | Creación, actualización, atención y reaparición de alertas | Pasó |

## 13. Comandos ejecutados

| Comando | Resultado real |
| ------- | -------------- |
| `uv run python manage.py check` | OK |
| `uv run python manage.py makemigrations --check` | OK |
| `uv run pytest apps/inventario -v` | `55 passed, 1 skipped` |

## 14. Archivos creados y modificados
- `apps/inventario/domain/consultas.py`
- `apps/inventario/domain/repositorios.py`
- `apps/inventario/infrastructure/repositories.py`
- `apps/inventario/application/services.py`
- `apps/inventario/presentation/serializers.py`
- `apps/inventario/presentation/views.py`
- `apps/inventario/tests/test_service.py`
- `apps/inventario/tests/test_alertas_api.py`
- `docs/historias/SDGT-62-alertas-stock-bajo.md`

## 15. Limitaciones y deuda técnica
- El frontend de alertas no se modificó por instrucción de alcance actual.
- LSP no está disponible en el entorno.

## 16. Conclusión
Backend completo; interfaz visual pendiente por restricción de alcance.
