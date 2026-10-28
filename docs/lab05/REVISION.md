# Revisión profunda del repositorio para el Laboratorio 05

## Alcance revisado

Se revisaron la estructura DDD, configuración de pruebas, dependencias, base de datos de integración, suite Python, módulo de pagos, Kanban y evidencias del laboratorio.

## Resultado de la revisión

| Área | Estado | Evidencia |
|---|---|---|
| Dependencias de pruebas | Conforme | `pyproject.toml` incluye pytest, pytest-cov y pytest-django |
| Separación de implementación y pruebas | Conforme | Código en `apps/`; pruebas en `tests/` y `apps/*/tests/` |
| Pruebas de dominio | Conforme | `tests/pagos/test_pago_dominio.py` |
| Pruebas del servicio de aplicación | Conforme | `tests/pagos/test_servicio_pagos.py` |
| Dobles de prueba | Conforme | `tests/pagos/test_servicio_pagos_doubles.py` |
| Integración/API | Conforme | `tests/pagos/test_api_pagos.py` y `test_repositorio_pagos.py` |
| Base PostgreSQL | Conforme | `compose.practica3.yml`, puerto local 55432 |
| Cobertura | Conforme | Umbral 85%; reporte generado con 87.90% para pagos |
| Kanban | Conforme | `docs/lab05/kanban.md` y `kanban-import.csv` |
| Documentación | Conforme | guía, diagrama, informe y referencias en `docs/lab05/` |
| Rama de entrega | Conforme | `laboratorio-05` publicada en GitHub; el trabajo no modifica `dev` ni `main` |

## Validación ejecutada

```bash
DB_NAME=software_textil_practica3 DB_PORT=55432 DB_HOST=127.0.0.1 \
  uv run pytest --junitxml=build/reports/pytest-lab05-full.xml
```

Resultado: **274 pruebas aprobadas, 0 fallos**.

La validación específica del módulo de pagos generó:

- `build/reports/pytest-lab05-full.xml`: reporte JUnit de la suite del laboratorio.
- `build/reports/coverage-lab05.xml`: cobertura de ramas del módulo de pagos; el umbral es 85%.

## Organización final

- `apps/`: implementación del sistema.
- `tests/` y `apps/*/tests/`: pruebas automatizadas.
- `docs/lab05/`: todos los entregables y evidencias del laboratorio 05.
- `build/reports/`: salidas generadas de pruebas y cobertura.
- `compose.practica3.yml`: PostgreSQL local aislado.
- `Makefile`: nuevo objetivo `make lab05` para repetir la validación.

Los archivos generados (`build/`, cachés, `.venv/`, `node_modules/`) permanecen ignorados por Git y no se mezclan con el código fuente.

## Hallazgos no bloqueantes

La revisión global de Ruff todavía informa 58 incidencias históricas en módulos de catálogo, inventario, pruebas existentes y `manage.py`. La prueba nueva del laboratorio 05 pasa Ruff sin incidencias. Esas incidencias previas no se modificaron porque refactorizarlas cambiaría el alcance funcional de otros laboratorios; quedan registradas para una tarea de saneamiento independiente.
