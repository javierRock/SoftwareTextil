# Laboratorio 05 — guía de trabajo local

1. Abrir `kanban.md` y mover las tarjetas según el flujo.
2. Ejecutar desde la raíz del clon local: `uv run pytest tests/pagos -q`.
3. Generar cobertura: `uv run pytest tests/pagos --cov=apps/ventas/pagos --cov-branch --cov-report=term-missing --cov-report=xml:build/reports/coverage.xml --junitxml=build/reports/pytest-lab05.xml`.
4. Guardar los reportes en `build/reports/` y completar el informe.
5. Para presentar el trabajo, mostrar el Kanban, el reporte de pruebas y el reporte de cobertura.

El clon local no tiene remoto configurado, por lo que estas acciones no publican ni alteran `javierRock/SoftwareTextil`.

## Diagrama de realización de objetivos

Consulta el [diagrama de realización](diagrama-realizacion-objetivos.md) para ver la relación entre objetivos, actividades, código y entregables.

## Revisión profunda

La [revisión profunda](REVISION.md) registra la auditoría de estructura, pruebas, cobertura, documentación y estado del repositorio.

## Tablero publicado

El tablero Kanban real está disponible en [GitHub Projects](https://github.com/users/carlosGCMP/projects/1). La rama y los Issues vinculados pertenecen exclusivamente al Laboratorio 05.

## Verificación frente a las instrucciones del laboratorio

- **Framework de pruebas:** pytest/pytest-django para Python, equivalente al framework xUnit solicitado para el lenguaje elegido.
- **Cobertura:** pytest-cov con cobertura de ramas y umbral mínimo de 85%.
- **Mocking:** `unittest.mock` (`MagicMock` y `create_autospec`).
- **Separación:** implementación en `apps/`; pruebas en `tests/` y `apps/*/tests/`.
- **Kanban:** proyecto público con las cinco columnas solicitadas e Issues #8–#14.
- **Responsables:** Carlos, Javier, Angelo/Yizens, Alejandro/Emilio y Lizzy están asignados en los Issues correspondientes.
- **Commits:** la rama publicada es `laboratorio-05` y sus mensajes describen cada cambio.
- **Reportes:** JUnit XML y cobertura XML generados en `build/reports/`.

## Automatización y TDD

- [Ciclo TDD y refactorización](tdd-refactorizacion.md)
- [Trazabilidad de Issues y commits](trazabilidad.md)
