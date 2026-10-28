# SDGT-59 — Stock agrupado por categoría

Ruta: `docs/historias/SDGT-59-stock-agrupado-categoria.md`

## 1. Objetivo

Se implementó el endpoint `GET /api/stock/por-categoria/` con filtro opcional `categoria_id` para devolver el stock actual agrupado por categoría.

## 2. Componentes involucrados

| Archivo o componente | Responsabilidad |
|---|---|
| `apps/inventario/presentation/views.py` | Expone la acción DRF `por_categoria`. |
| `apps/inventario/presentation/serializers.py` | Serializa la respuesta agrupada. |
| `apps/inventario/application/services.py` | Orquesta la consulta y valida la categoría. |
| `apps/inventario/infrastructure/repositories.py` | Consulta ORM y agrupa por categoría sin N+1. |
| `apps/inventario/domain/consultas.py` | DTOs de respuesta. |
| `apps/inventario/domain/excepciones.py` | Error de categoría inexistente. |

## 3. Implementación

El flujo quedó en capas: la view recibe el query param, el servicio valida la categoría y el repositorio consulta `StockPrendaModel` y `PrendaModel` en lote para construir la agrupación por categoría.

## 4. Estilos de programación usados

| Estilo | Estado | Evidencia | Justificación |
|---|---|---|---|
| Pipeline | Aplicado | `views.py` → `services.py` → `repositories.py` → `serializers.py` | La consulta fluye por capas sin ORM en la view. |
| Error/Exception Handling | Aplicado | `CategoriaNoEncontrada` y mapeo a 404 | La categoría inválida no se oculta. |
| RESTful | Verificado | `@action(detail=False, methods=["get"], url_path="por-categoria")` | El endpoint usa GET y no modifica datos. |

Archivo `apps/inventario/application/services.py`:

```python
    def listar_stock_por_categoria(self, categoria_id: str | None = None) -> list[CategoriaStockAgrupada]:
        if categoria_id and self.repo_catalogo is not None and self.repo_catalogo.buscar_categoria(categoria_id) is None:
            raise CategoriaNoEncontrada("La categoria no existe")
        return self.repo_inventario.listar_por_categoria(categoria_id)
```

Archivo `apps/inventario/infrastructure/repositories.py`:

```python
        prendas = PrendaModel.objects.select_related("categoria").filter(id__in=[stock.prenda_id for stock in stocks])
        if categoria_id:
            prendas = prendas.filter(categoria_id=categoria_id)

        prendas_por_id = {str(prenda.id): prenda for prenda in prendas}
        agrupados: dict[str, dict[str, object]] = {}
```

## 5. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
|---|---|---|
| Nombres | `listar_stock_por_categoria`, `CategoriaStockAgrupada` | Nombres explícitos del caso de uso. |
| Funciones | Separación entre validación, consulta y serialización | Cada capa hace una sola cosa. |
| Estructura del código fuente | Dominio → aplicación → infraestructura → presentación | Flujo alineado con la arquitectura existente. |
| Objetos y estructuras de datos | DTOs `CategoriaStockAgrupada` y `PrendaStockAgrupada` | La respuesta no depende del ORM. |
| Tratamiento de errores | `CategoriaNoEncontrada` | El 404 se resuelve de forma explícita. |

## 6. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
|---|---|---|---|
| Limitación estructural | `StockPrendaModel` no tiene FK a `PrendaModel` | Se resolvió con carga en lote y mapa por ID | Corregido |

## 7. SonarLint y análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
|---|---|---|---|
| Revisión manual | No verificado | Sin hallazgos manuales adicionales | N/A |

## 8. Pruebas

| Prueba | Comportamiento | Resultado |
|---|---|---|
| `pytest apps/inventario -v` | Valida backend inventario y la nueva consulta | 44 passed, 1 skipped |

## 9. Comandos ejecutados

| Comando | Resultado |
|---|---|
| `uv run python manage.py check` | Sin issues |
| `uv run python manage.py makemigrations --check` | No changes detected |
| `uv run pytest apps/inventario -v` | 44 passed, 1 skipped |
| `uv run python manage.py test apps/inventario` | 1 test, OK (skipped=1) |

## 10. Archivos creados y modificados

- `apps/catalogo/domain/repositorios.py`
- `apps/inventario/domain/excepciones.py`
- `apps/inventario/domain/consultas.py`
- `apps/inventario/domain/repositorios.py`
- `apps/inventario/infrastructure/repositories.py`
- `apps/inventario/application/services.py`
- `apps/inventario/presentation/serializers.py`
- `apps/inventario/presentation/views.py`
- `apps/inventario/tests/conftest.py`
- `apps/inventario/tests/test_stock_por_categoria.py`

## 11. Limitaciones

- `StockPrendaModel` sigue sin FK directa a `PrendaModel`.
- La categoría inexistente se resuelve como 404, siguiendo la convención usada por el módulo.

## 12. Conclusión

La consulta agrupada quedó implementada, filtrable y sin N+1 en la capa de presentación.
