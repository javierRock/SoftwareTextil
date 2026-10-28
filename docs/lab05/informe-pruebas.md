# Informe de pruebas — Laboratorio 05

## Alcance

Se seleccionó el módulo `apps/ventas/pagos` del repositorio SoftwareTextil. Las pruebas cubren el agregado de dominio `Pago`, el servicio de aplicación `ServicioPagos`, los repositorios y la API. La prueba adicional del laboratorio usa `unittest.mock.create_autospec` y `MagicMock` para aislar los puertos de persistencia y la unidad de trabajo.

## Ejecución reproducible

Desde la raíz de `SoftwareTextil_Lab05_Local`:

```bash
DB_NAME=software_textil_practica3 DB_PORT=55432 docker compose -p softwaretextil-lab05 -f compose.practica3.yml up -d --wait db
DB_NAME=software_textil_practica3 DB_PORT=55432 DB_HOST=127.0.0.1 \
  uv run python manage.py migrate --noinput
DB_NAME=software_textil_practica3 DB_PORT=55432 DB_HOST=127.0.0.1 \
  uv run pytest tests/pagos \
    --cov=apps/ventas/pagos --cov-branch \
    --cov-report=term-missing \
    --cov-report=xml:build/reports/coverage-lab05.xml \
    --junitxml=build/reports/pytest-lab05.xml
```

## Resultado

- Fecha de ejecución: 28-10-2026.
- Pruebas recopiladas: 54.
- Pruebas aprobadas: 54.
- Pruebas fallidas: 0.
- Cobertura total: 87.90% con ramas.
- Umbral configurado: 85%.
- Resultado: **PASS**.

## Evidencias generadas

- `build/reports/pytest-lab05.xml`: reporte JUnit de ejecución.
- `build/reports/coverage-lab05.xml`: reporte XML de cobertura.
- `tests/pagos/test_servicio_pagos_doubles.py`: casos con dobles de prueba.
- `docs/lab05/kanban.md`: tablero y trazabilidad de las tarjetas.

## Observación sobre el alcance

La base PostgreSQL se ejecuta en el contenedor local `softwaretextil-lab05-db-1`, publicado en el puerto `55432`. El contenedor pertenece al laboratorio y se puede detener con:

```bash
docker compose -p softwaretextil-lab05 -f compose.practica3.yml down
```
