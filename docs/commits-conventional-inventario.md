# Commits propuestos con Conventional Commits

Este documento resume la secuencia de commits que se aplicaría para dejar el trabajo de `apps/inventario/` con historial limpio y atómico.

## Secuencia propuesta

| Orden | Commit | Alcance |
|---|---|---|
| 1 | `feat(inventario): agregar excepciones de dominio y reglas de stock` | `apps/inventario/domain/excepciones.py`, `apps/inventario/domain/stock_prenda.py`, `apps/inventario/domain/repositorios.py` |
| 2 | `feat(inventario): hacer atomicos los ingresos y salidas de stock` | `apps/inventario/application/services.py`, `apps/inventario/infrastructure/repositories.py` |
| 3 | `feat(inventario): ajustar serializers y respuestas de api` | `apps/inventario/presentation/serializers.py`, `apps/inventario/presentation/views.py` |
| 4 | `test(inventario): cubrir ingresos, salidas y rollback transaccional` | `apps/inventario/tests/test_domain.py`, `apps/inventario/tests/test_service.py`, `apps/inventario/tests/test_api.py`, `apps/inventario/tests/test_concurrency.py`, `apps/inventario/tests/conftest.py` |

## Criterio usado

- Cada commit agrupa archivos que dependen entre sí.
- El dominio va primero, luego aplicación/infraestructura, después presentación y por último pruebas.
- Los mensajes siguen `type(scope): description`.

## Observación

Si se quisiera partir todavía más el historial, el commit de pruebas podría separarse en:

- `test(inventario): agregar pruebas de dominio y servicio`
- `test(inventario): agregar pruebas de api y concurrencia`

Pero para esta rama, la secuencia anterior mantiene un equilibrio razonable entre atomicidad y legibilidad.
