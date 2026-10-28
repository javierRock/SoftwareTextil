# SDGT-67 — HF 3.3: Generar reporte del inventario actual

## 1. Objetivo
Generar un reporte descargable del inventario actual, reutilizando la consulta agrupada por categoría y valorizando cada prenda con el precio del catálogo.

## 2. Estado inicial
No existía un reporte operativo en el backend. Tampoco había librería de PDF instalada. Sí existía la consulta de stock por categoría y el catálogo con `precio_monto`/`precio_moneda`, por lo que el reporte pudo construirse sin inventar nuevos datos.

## 3. Subtareas

| Subtarea | Descripción | Estado | Evidencia |
| -------- | ----------- | ------ | --------- |
| SDGT-68 | Interfaz de reportes con filtros y descarga | Parcial | Backend listo; frontend no modificado por instrucción actual |
| SDGT-69 | Backend para reporte consolidado en PDF y Excel | Completa | `ServicioReporteInventario`, `StockViewSet.reporte()` |
| SDGT-70 | Validar cantidades y valorización | Completa | `test_reportes_api.py` |
| SDGT-71 | Validar generación, descarga e integridad | Completa | `test_reportes_api.py` |

## 4. Componentes involucrados

| Archivo o componente | Responsabilidad |
| -------------------- | --------------- |
| `apps/inventario/application/reportes.py` | Construcción y exportación del reporte |
| `apps/inventario/application/services.py` | Reuso de la consulta de stock por categoría |
| `apps/inventario/presentation/views.py` | Endpoint `reporte` |
| `apps/catalogo/infrastructure/repositories.py` | Obtención de precios reales |
| `apps/inventario/tests/test_reportes_api.py` | Validación de PDF, XLSX e integridad |

## 5. Implementación
El flujo parte de `GET /api/stock/reporte/?formato=pdf|xlsx[&categoria_id=...]`. El servicio obtiene el resumen por categoría, cruza cada prenda con su precio real de catálogo, calcula valorizaciones y devuelve un archivo descargable. El XLSX se generó con la biblioteca estándar para no añadir dependencias; el PDF se generó con un emisor mínimo válido.

## 6. Conflictos y compatibilidad
- Se reutilizó la consulta agrupada ya probada en `SDGT-59` y `SDGT-60`.
- No se agregó costo artificial: el reporte usa `precio_monto` y `precio_moneda` reales del catálogo.
- **Corrección de dependencia detectada durante SDGT-67:** se evitó introducir `openpyxl` en el venv y se construyó el XLSX con stdlib.
- No se altera la base de datos.

## 7. Estilos de programación

| Estilo | Estado | Evidencia | Justificación |
| ------ | ------ | --------- | ------------- |
| Things | Verificado | `apps/inventario/application/reportes.py` | El servicio mantiene el estado del reporte y sus salidas. |
| Pipeline | Verificado | `apps/inventario/presentation/views.py` | Query params → servicio → archivo → respuesta HTTP. |
| Error/Exception Handling | Verificado | `apps/inventario/presentation/views.py` | Formatos inválidos y categorías inexistentes se traducen a HTTP. |
| Persistent-Tables | Verificado | `apps/inventario/infrastructure/repositories.py` | El reporte usa consultas sobre tablas reales. |
| RESTful | Verificado | `apps/inventario/presentation/views.py` | El reporte se expone como recurso descargable. |
| Lazy-Rivers | No aplicable | N/A | No hay generadores de flujo en este reporte. |
| Trinity | No aplicable | N/A | No se aplicó un patrón de tres partes separado. |

**Things**
```python
class ServicioReporteInventario:
    def __init__(self, servicio_inventario: ServicioInventario, repo_prenda: RepositorioPrenda) -> None:
        self.servicio_inventario = servicio_inventario
        self.repo_prenda = repo_prenda
```
Ruta: `apps/inventario/application/reportes.py`

**Pipeline**
```python
serializer = ReporteInventarioQuerySerializer(data=request.query_params)
serializer.is_valid(raise_exception=True)
archivo = servicio.generar_archivo(
    formato=serializer.validated_data["formato"],
    categoria_id=serializer.validated_data.get("categoria_id") or None,
)
```
Ruta: `apps/inventario/presentation/views.py`

**Error/Exception Handling**
```python
except (CategoriaNoEncontrada, ValueError) as exc:
    body, code = _manejar_error(exc)
    return Response(body, status=code)
```
Ruta: `apps/inventario/presentation/views.py`

**Persistent-Tables**
```python
resumen = self.servicio_inventario.listar_stock_por_categoria(categoria_id)
prendas_catalogo = {str(prenda.id): prenda for prenda in self.repo_prenda.listar()}
```
Ruta: `apps/inventario/application/reportes.py`

**RESTful**
```python
@action(detail=False, methods=["get"], url_path="reporte")
def reporte(self, request):
```
Ruta: `apps/inventario/presentation/views.py`

## 8. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
| --------- | -------- | --------- |
| Nombres | `ServicioReporteInventario`, `ArchivoReporte` | `apps/inventario/application/reportes.py` |
| Funciones | `generar_archivo()` separa formato de construcción | `apps/inventario/application/reportes.py` |
| Estructura | Reuso de servicio y repositorio, no lógica en vista | `apps/inventario/presentation/views.py` |
| Manejo de errores | Formato inválido y categoría inexistente vuelven 400/404 | `apps/inventario/presentation/views.py` |
| Separación de responsabilidades | El servicio arma el archivo; la vista solo descarga | `apps/inventario/application/reportes.py` |
| Ausencia de duplicación | Se reutiliza la consulta de inventario existente | `apps/inventario/application/services.py` |

## 9. Arquitectura y decisiones
- El reporte no consulta la base por su cuenta: reusa el servicio de inventario.
- La valorización usa el precio real del catálogo, no un costo inventado.
- El XLSX se construye con stdlib para no añadir dependencias.
- El PDF generado es mínimo pero válido para descarga.
- El filtro por categoría usa la validación ya existente del catálogo.

## 10. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
| ---- | -------- | ---------- | ------ |
| Dependencia | El entorno no tenía `openpyxl` | Se reemplazó por generación XLSX con stdlib | Corregido |

## 11. Análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
| ----------- | ------- | -------- | ---------- |
| Revisión manual | No verificado | Ninguno nuevo en esta historia | N/A |
| LSP | No verificado | LSP no disponible en el entorno | N/A |

## 12. Pruebas

| Prueba | Comportamiento | Resultado |
| ------ | -------------- | --------- |
| `test_reportes_api.py` | XLSX legible, PDF legible, filtro, vacío, permisos | Pasó |
| `test_stock_por_categoria.py` | Fuente del reporte y no mutación de la BD | Pasó |

## 13. Comandos ejecutados

| Comando | Resultado real |
| ------- | -------------- |
| `uv run python manage.py check` | OK |
| `uv run python manage.py makemigrations --check` | OK |
| `uv run pytest apps/inventario -v` | `55 passed, 1 skipped` |

## 14. Archivos creados y modificados
- `apps/inventario/application/reportes.py`
- `apps/inventario/application/services.py`
- `apps/inventario/presentation/serializers.py`
- `apps/inventario/presentation/views.py`
- `apps/inventario/tests/test_reportes_api.py`
- `docs/historias/SDGT-67-reporte-inventario.md`

## 15. Limitaciones y deuda técnica
- El frontend de reportes no se modificó por instrucción de alcance actual.
- El PDF es mínimo; cubre descarga e integridad, no maquetación avanzada.

## 16. Conclusión
Backend completo; interfaz visual pendiente por restricción de alcance.
