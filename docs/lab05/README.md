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
