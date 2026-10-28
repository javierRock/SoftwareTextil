# SDGT-60 — Pruebas de exactitud del stock agrupado

Ruta: `docs/historias/SDGT-60-pruebas-stock-agrupado.md`

## 1. Objetivo

Se agregaron pruebas automatizadas para asegurar que el endpoint agrupado devuelva cantidades exactas, filtre correctamente y respete el estado real de la base de datos.

## 2. Componentes involucrados

| Archivo o componente | Responsabilidad |
|---|---|
| `apps/inventario/tests/test_stock_por_categoria.py` | Casos funcionales del endpoint. |
| `apps/inventario/tests/conftest.py` | Fixtures compartidas con el resto del módulo. |
| `apps/inventario/tests/test_api.py` | Flujo de ingreso/salida usado por varias pruebas. |

## 3. Implementación

Se cubrieron 15 escenarios con datos propios por prueba: una o varias categorías, stock cero, categoría sin stock, categoría inexistente, filtro, respuesta vacía, cambios tras ingreso/salida y control de consultas para evitar N+1.

## 4. Estilos de programación usados

| Estilo | Estado | Evidencia | Justificación |
|---|---|---|---|
| Pipeline | Verificado | Pruebas que ejercitan `view -> service -> repository` | Se valida el flujo real. |
| Error/Exception Handling | Verificado | Caso `categoria_id` inexistente | Se verifica el 404 esperado. |
| RESTful | Verificado | GET puro sin cambios de estado | La consulta no modifica datos. |

Archivo `apps/inventario/tests/test_stock_por_categoria.py`:

```python
@pytest.mark.django_db
def test_no_existe_problema_n_mas_uno(client, django_assert_num_queries) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    for indice in range(5):
        _crear_prenda(prenda_id=f"prenda-{indice}", nombre=f"Camisa {indice}", categoria=categoria, stock=indice + 1)

    with django_assert_num_queries(2):
        respuesta = client.get("/api/stock/por-categoria/")
```

## 5. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
|---|---|---|
| Nombres | `test_consulta_despues_de_registrar_un_ingreso` | El nombre describe el caso de negocio. |
| Funciones | Helpers `_crear_categoria` y `_crear_prenda` | Evitan duplicación de datos de prueba. |
| Estructura del código fuente | Archivo dedicado por historia | Las pruebas del endpoint quedan aisladas. |
| Objetos y estructuras de datos | Fixtures y helpers explícitos | Cada prueba crea sus propios datos. |
| Tratamiento de errores | Verificación de 404 y 400 | El contrato de error se valida. |

## 6. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
|---|---|---|---|
| Riesgo de regresión | Cambios en ingreso/salida podían alterar stock agrupado | Pruebas post-ingreso y post-salida | Corregido |

## 7. SonarLint y análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
|---|---|---|---|
| Revisión manual | No verificado | Sin hallazgos adicionales | N/A |

## 8. Pruebas

| Prueba | Comportamiento | Resultado |
|---|---|---|
| Endpoint agrupado | 15 casos de exactitud y contrato | 15/15 verdes |
| N+1 | 5 prendas con 2 consultas | Verificado |

## 9. Comandos ejecutados

| Comando | Resultado |
|---|---|
| `uv run pytest apps/inventario -v` | 44 passed, 1 skipped |
| `uv run python manage.py test apps/inventario` | 1 test, OK (skipped=1) |

## 10. Archivos creados y modificados

- `apps/inventario/tests/test_stock_por_categoria.py`
- `apps/inventario/tests/conftest.py`

## 11. Limitaciones

- La exactitud depende de que el estado de prueba cree los modelos relacionados de forma consistente.

## 12. Conclusión

El endpoint quedó cubierto con pruebas de negocio, contrato y rendimiento lógico.
