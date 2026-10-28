# Informe de pruebas — Laboratorio 05

## Alcance

Se seleccionó el módulo `apps/ventas/pagos` del repositorio SoftwareTextil. Las pruebas cubren el agregado de dominio `Pago`, el servicio de aplicación `ServicioPagos`, los repositorios y la API. La prueba adicional del laboratorio usa `unittest.mock.create_autospec` y `MagicMock` para aislar los puertos de persistencia y la unidad de trabajo.

## Ejecución reproducible

Desde la raíz de la rama `laboratorio-05` del repositorio:

```bash
make db-up
make lab05
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

- `build/reports/pytest-lab05-full.xml`: reporte JUnit de ejecución.
- `build/reports/coverage-lab05.xml`: reporte XML de cobertura.
- `tests/pagos/test_servicio_pagos_doubles.py`: casos con dobles de prueba.
- `docs/lab05/kanban.md`: tablero y trazabilidad de las tarjetas.

## Observación sobre el alcance

La base PostgreSQL se ejecuta en el contenedor local `softwaretextil-lab05-db-1`, publicado en el puerto `55432`. El contenedor pertenece al laboratorio y se puede detener con:

```bash
make db-down
```
