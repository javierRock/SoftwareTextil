# Tareas de @Angel-Cs2004

Responsable de Pedidos, Ventas y Rutas. Cada tarea siguió el ciclo TDD: primero se publicó la prueba que falla (RED), luego el refactor que la hace pasar (GREEN) y al final se ejecutó la suite completa.

| Smell, bug o vulnerabilidad | Categoría | Descripción | Módulo o componente | Responsable | Prioridad | Estrategia de refactoring |
| --- | --- | --- | --- | --- | --- | --- |
| Q-01 · [#47](https://github.com/javierRock/SoftwareTextil/issues/47) | Clean Code (DRY) y bug de confiabilidad | Reserva y liberación repetían el bloqueo y la validación de stock. La versión con generador guardaba cada variante antes de validar la siguiente y dejaba escrituras parciales. | Pedidos · `apps/ventas/pedidos/application/services.py` | @Angel-Cs2004 | Media | Extract Method (`_ajustar_stocks`, `_bloquear_stocks`) y Parameterize Method (el ajuste se recibe como función). Primero se bloquea y valida todo, luego se ajusta en memoria y al final se persiste. |
| S-02 · [#64](https://github.com/javierRock/SoftwareTextil/issues/64) | Clean Code (literal repetido, SonarQube `python:S1192`) | `"usuarios.UsuarioModel"` se repetía en las claves foráneas de catálogo, inventario y ventas. | Ventas y compartido · `apps/compartido/infrastructure/models.py` | @Angel-Cs2004 | Baja | Replace Magic Literal with Symbolic Constant y Move Field: `MODELO_USUARIO` vive en el módulo compartido. |
| S-03 · [#65](https://github.com/javierRock/SoftwareTextil/issues/65) | Clean Code (literal repetido, SonarQube `python:S1192`) y OCP | Cada módulo de ventas repetía su `path("api/ventas/", include(...))`. | Rutas · `config/urls.py` | @Angel-Cs2004 | Baja | Replace Magic Literal with Symbolic Constant y Consolidate Duplicate Fragments: `MODULOS_VENTAS` fija el orden y genera los `include`. |

## Casos de prueba

| ID | Valores de prueba | Acción | Resultado esperado | Archivo |
| --- | --- | --- | --- | --- |
| Q-01 | Carrito o pedido con variantes `c`, `a`, `b` | Generar pedido y luego cancelarlo | Ambas operaciones bloquean en el orden `a`, `b`, `c` | `tests/ventas/test_servicio_pedidos_mocks.py` |
| Q-01 | Cantidades 1, 2 y 3 | Generar y cancelar | Cada stock se reserva y libera con su cantidad; total 72,00 y estado conservados | `tests/ventas/test_servicio_pedidos_mocks.py` |
| Q-01 | Variante `c` sin stock | Generar o cancelar | `StockNoEncontradoError`; ningún stock modificado ni guardado | `tests/ventas/test_servicio_pedidos_mocks.py` |
| Q-01 | `reservar` de `c` lanza `StockInsuficienteError` | Generar | Error propagado; ningún stock ni pedido guardado | `tests/ventas/test_servicio_pedidos_mocks.py` |
| Q-01 | Servicio sin inventario | Generar y cancelar | No consulta ni guarda stock | `tests/ventas/test_servicio_pedidos_mocks.py` |
| S-02 | Cinco claves foráneas hacia el usuario | Inspeccionar `_meta` | Todas apuntan a `UsuarioModel` | `tests/compartido/test_referencia_modelo_usuario.py` |
| S-02 | `models.py` de catálogo, inventario y ventas | Leer el fuente | No contienen el literal del modelo | `tests/compartido/test_referencia_modelo_usuario.py` |
| S-02 | Esquema actual | `makemigrations --check --dry-run` | `No changes detected` | `tests/compartido/test_referencia_modelo_usuario.py` |
| S-03 | `/api/ventas/{carritos,pedidos,pagos,despachos}/` | `resolve` y `reverse` | Cada ruta resuelve a su módulo | `tests/ventas/test_rutas_ventas.py` |
| S-03 | `urlpatterns` | Recorrer las inclusiones | Orden carrito, pedidos, pagos, despachos, antes del fallback `spa` | `tests/ventas/test_rutas_ventas.py` |
| S-03 | `config/urls.py` | Leer el fuente | El prefijo y su `path` se declaran una sola vez | `tests/ventas/test_rutas_ventas.py` |

## Ejecución RED → GREEN

| Tarea | RED | GREEN |
| --- | --- | --- |
| Q-01 | [3 fallos de 7](../evidencias/tdd-angel-cs2004/q01-red.txt): se guardaban 2 stocks antes del error | [13 aprobadas](../evidencias/tdd-angel-cs2004/q01-green.txt) |
| S-02 | [Error de importación](../evidencias/tdd-angel-cs2004/s02-red.txt): la constante compartida no existía | [10 aprobadas](../evidencias/tdd-angel-cs2004/s02-green.txt) |
| S-03 | [1 fallo de 7](../evidencias/tdd-angel-cs2004/s03-red.txt): 4 llamadas `path(RUTA_VENTAS, ...)` | [7 aprobadas](../evidencias/tdd-angel-cs2004/s03-green.txt) |

La [suite completa](../evidencias/tdd-angel-cs2004/suite-completa.txt) pasó de 419 a 436 pruebas aprobadas contra PostgreSQL. `makemigrations --check --dry-run` no detecta cambios.

## Commits

| Tarea | Prueba (RED) | Refactor (GREEN) |
| --- | --- | --- |
| Q-01 · #47 | [`159939b`](https://github.com/javierRock/SoftwareTextil/commit/159939b) | [`160a089`](https://github.com/javierRock/SoftwareTextil/commit/160a089) |
| S-02 · #64 | [`e4ab80f`](https://github.com/javierRock/SoftwareTextil/commit/e4ab80f) | [`c861d9d`](https://github.com/javierRock/SoftwareTextil/commit/c861d9d) |
| S-03 · #65 | [`966faeb`](https://github.com/javierRock/SoftwareTextil/commit/966faeb) | [`3e966eb`](https://github.com/javierRock/SoftwareTextil/commit/3e966eb) |

El commit base de la rama [`ff73eea`](https://github.com/javierRock/SoftwareTextil/commit/ff73eeaa3420f7e18749dbf046647e98763730a9) introdujo la primera extracción. Estos commits agregan las pruebas, corrigen las escrituras parciales y completan las tres tareas. Las tarjetas pasan a **DONE** en el [Kanban](https://github.com/users/javierRock/projects/2/views/1).
