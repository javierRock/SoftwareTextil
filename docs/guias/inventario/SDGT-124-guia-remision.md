# SDGT-124 — HF 6.4: Generar guía de remisión o documento de despacho

## 1. Objetivo
Emitir un documento de despacho a partir de un caso persistido sin volver a descontar stock.

## 2. Estado inicial
El repositorio solo tiene `cliente_id`, `pedido_id` y detalle de pedido/carrito. No existen modelos reales de cliente, dirección ni despacho persistido. La documentación UML menciona despachos, pero el código ejecutable no los implementa.

## 3. Subtareas

| Subtarea | Descripción | Estado | Evidencia |
| -------- | ----------- | ------ | --------- |
| SDGT-125 | Interfaz y backend para generar la guía en PDF | Bloqueada | Faltan modelos de dominio y persistencia |
| SDGT-126 | Validar cliente, prendas y cantidades | Bloqueada | No existe entidad de cliente/dirección que validar |

## 4. Componentes involucrados

| Archivo o componente | Responsabilidad |
| -------------------- | --------------- |
| `apps/ventas/models.py` | Solo guarda IDs; no modela cliente ni dirección reales |
| `apps/ventas/pedidos/domain/pedido.py` | Pedido persistido y detalles |
| `apps/compartido/domain/enums.py` | `EstadoDespacho` existe como enum aislado |
| `docs/modelo_dominio.md` | Referencia UML no implementada en código |

## 5. Implementación
No se implementó código porque no hay una entidad persistida de despacho ni datos suficientes para emitir legalmente una guía sin inventar campos. La única salida correcta con el estado actual es documentar la limitación y esperar el modelo real de despacho/cliente/dirección.

## 6. Conflictos y compatibilidad
- No se inventaron modelos, relaciones ni endpoints.
- No se tocó inventario para evitar una segunda reducción del stock.
- El documento de remisión solo podrá salir cuando exista una entidad persistida real.

## 7. Estilos de programación

| Estilo | Estado | Evidencia | Justificación |
| ------ | ------ | --------- | ------------- |
| Things | No aplicable | N/A | No hubo implementación nueva. |
| Pipeline | No aplicable | N/A | No hubo flujo nuevo en código. |
| Error/Exception Handling | No aplicable | N/A | No hubo cambios en manejo de errores. |
| Persistent-Tables | No aplicable | N/A | No se creó persistencia nueva. |
| RESTful | No aplicable | N/A | No se añadió endpoint. |
| Lazy-Rivers | No aplicable | N/A | No se añadió procesamiento perezoso. |
| Trinity | No aplicable | N/A | No se introdujo patrón nuevo. |

## 8. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
| --------- | -------- | --------- |
| Nombres | `EstadoDespacho`, `PedidoModel` | Modelos existentes |
| Funciones | No aplica | N/A |
| Estructura | No aplica | N/A |
| Manejo de errores | No aplica | N/A |
| Separación de responsabilidades | Se evita mezclar ventas con inventario | Código existente |
| Ausencia de duplicación | No se agrega código duplicado | N/A |

## 9. Arquitectura y decisiones
- Se validó la inexistencia de `apps/despachos/`.
- Solo existe `cliente_id`; no hay entidad de cliente ni dirección.
- La historia queda bloqueada por falta de modelo de dominio, no por falta de tiempo.

## 10. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
| ---- | -------- | ---------- | ------ |
| Bloqueo de dominio | No hay cliente/dirección/despacho persistido | No aplicable hasta crear el modelo | Bloqueado |

## 11. Análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
| ----------- | ------- | -------- | ---------- |
| Revisión manual | No verificado | Falta el modelo requerido | N/A |
| LSP | No verificado | LSP no disponible en el entorno | N/A |

## 12. Pruebas

| Prueba | Comportamiento | Resultado |
| ------ | -------------- | --------- |
| Auditoría de modelos | Verificación de cliente/dirección/despacho | Bloqueada por ausencia de modelo |
| `pytest apps/inventario -v` | Regresión de inventario | Pasó |

## 13. Comandos ejecutados

| Comando | Resultado real |
| ------- | -------------- |
| `uv run python manage.py check` | OK |
| `uv run python manage.py makemigrations --check` | OK |
| `uv run pytest apps/inventario -v` | `55 passed, 1 skipped` |

## 14. Archivos creados y modificados
- `docs/historias/SDGT-124-guia-remision.md`

## 15. Limitaciones y deuda técnica
- Falta app o modelo persistido de despacho.
- Falta modelo real de cliente y dirección.
- No se debe forzar una guía legal con `cliente_id` aislado.

## 16. Conclusión
Historia bloqueada por ausencia de modelos y contratos de dominio.
