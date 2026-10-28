# Diagrama de realización de objetivos — Laboratorio 05

El siguiente flujo muestra cómo se cumplen los objetivos del laboratorio dentro de `SoftwareTextil`, desde la planificación Kanban hasta la evidencia final.

```mermaid
flowchart TD
    A[Objetivo del laboratorio 05\nAutomatizar pruebas unitarias e integración] --> B[Preparar entorno local]
    B --> B1[Python 3.11 + uv]
    B --> B2[pytest + pytest-cov]
    B --> B3[PostgreSQL local aislado]

    A --> C[Organizar trabajo con Kanban]
    C --> C1[TO-DO]
    C --> C2[CURRENT ITERATION]
    C --> C3[IN PROGRESS]
    C --> C4[FIX VALIDATION]
    C --> C5[DONE]

    C --> D[Convertir tareas en Issues]
    D --> D1[Descripción]
    D --> D2[Responsable]
    D --> D3[Etiqueta]
    D --> D4[Duración]

    A --> E[Pruebas del dominio]
    E --> E1[Agregado Pago]
    E1 --> E2[Invariantes y reglas]
    E2 --> E3[Arrange / Act / Assert]

    A --> F[Pruebas del servicio de aplicación]
    F --> F1[ServicioPagos]
    F1 --> F2[Mock de repositorio de pagos]
    F1 --> F3[Mock de repositorio de pedidos]
    F1 --> F4[Mock de unidad de trabajo]
    F2 --> F5[Verificar llamadas e interacciones]
    F3 --> F5
    F4 --> F5

    E3 --> G[Ejecutar suite de pruebas]
    F5 --> G
    G --> G1[Pruebas unitarias]
    G --> G2[Pruebas de integración/API]
    G --> G3[Corrección y refactorización]

    G --> H[Medir resultados]
    H --> H1[Reporte JUnit XML]
    H --> H2[Reporte de cobertura XML]
    H2 --> H3[Umbral mínimo 85%]

    H1 --> I[Entregables del laboratorio]
    H3 --> I
    C5 --> I
    I --> I1[Código de pruebas en el repositorio]
    I --> I2[Informe de ejecución]
    I --> I3[Reporte de cobertura]
    I --> I4[Capturas del Kanban y resultados]
```

## Trazabilidad en el repositorio

| Objetivo | Implementación | Evidencia |
|---|---|---|
| Organizar el trabajo | `docs/lab05/kanban.md` y `kanban-import.csv` | Tablero y tarjetas |
| Probar reglas del dominio | `tests/pagos/test_pago_dominio.py` | Casos del agregado `Pago` |
| Probar servicios con dobles | `tests/pagos/test_servicio_pagos_doubles.py` | `Mock`, `MagicMock` y `create_autospec` |
| Probar integración y API | `tests/pagos/test_api_pagos.py` y `test_repositorio_pagos.py` | 54 pruebas aprobadas |
| Medir cobertura | `build/reports/coverage-lab05.xml` | 87.90% de cobertura |
| Reportar ejecución | `build/reports/pytest-lab05.xml` y `docs/lab05/informe-pruebas.md` | Informe JUnit y resumen |

## Comando que reproduce el flujo técnico

```bash
DB_NAME=software_textil_practica3 DB_PORT=55432 \
  docker compose -p softwaretextil-lab05 -f compose.practica3.yml up -d --wait db

DB_NAME=software_textil_practica3 DB_PORT=55432 DB_HOST=127.0.0.1 \
  uv run pytest tests/pagos \
  --cov=apps/ventas/pagos --cov-branch \
  --cov-report=xml:build/reports/coverage-lab05.xml \
  --junitxml=build/reports/pytest-lab05.xml
```
