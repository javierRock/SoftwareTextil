# Quality & Automation — pruebas unitarias, dobles y automatización

Esta entrega se ejecuta en la rama `testing-automation` sobre el proyecto Django real. El módulo elegido es `apps/ventas/pagos`; la implementación permanece en `apps/` y las pruebas en `tests/` y `apps/*/tests/`.

## Ejecución local

Desde la raíz del repositorio:

```bash
uv sync --locked --python 3.11
make quality
```

`make quality` levanta un PostgreSQL aislado con `compose.quality.yml`, ejecuta la suite con `pytest`, mide cobertura de ramas con `pytest-cov` y escribe los reportes JUnit/XML en `build/reports/`. El umbral mínimo configurado es 85%. Al terminar, se puede detener la base con `make db-down`.

## Entregables

- [Kanban y tarjetas](kanban.md)
- [Diagrama de realización de objetivos](diagrama-realizacion-objetivos.md)
- [Informe de pruebas](informe-pruebas.md)
- [Revisión profunda](REVISION.md)
- [Ciclo TDD y refactorización](tdd-refactorizacion.md)
- [Trazabilidad de Issues y commits](trazabilidad.md)
- `tests/pagos/test_servicio_pagos_doubles.py`: pruebas con dobles de persistencia y unidad de trabajo
- `build/reports/pytest-quality-full.xml`: reporte JUnit generado
- `build/reports/coverage-quality.xml`: reporte XML de cobertura generado

## Correspondencia con los objetivos

- **Framework xUnit:** pytest y pytest-django para Python.
- **Cobertura:** pytest-cov con ramas y `fail_under = 85` en `pyproject.toml`.
- **Mocking:** `unittest.mock`, usando `MagicMock` y `create_autospec`.
- **Separación:** código productivo en `apps/` y pruebas en `tests/`/`apps/*/tests/`.
- **TDD:** ciclo Red-Green-Refactor documentado para `ServicioPagos`.
- **Kanban:** proyecto público con `TO-DO`, `CURRENT ITERATION`, `IN PROGRESS`, `FIX VALIDATION` y `DONE`.
- **Automatización:** objetivo `make quality` y `Jenkinsfile` para ejecutar build, validaciones, pruebas y archivar reportes.
- **Trazabilidad:** Issues #8–#19 enlazados al proyecto y commits descriptivos en esta rama.

## Tablero y rama publicados

- [Proyecto Kanban de SoftwareTextil](https://github.com/users/carlosGCMP/projects/1)
- [Rama `testing-automation`](https://github.com/javierRock/SoftwareTextil/tree/testing-automation)
- [Issues del repositorio](https://github.com/javierRock/SoftwareTextil/issues)
