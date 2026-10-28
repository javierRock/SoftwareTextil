# Kanban local — Pruebas y automatización

Este tablero reproduce la plantilla Kanban solicitada en el flujo de calidad y sirve como respaldo local. No se conecta ni publica cambios en GitHub.

**Repositorio de trabajo:** `javierRock/SoftwareTextil`
**Rama:** `testing-automation`
**Módulo seleccionado:** `apps/ventas/pagos`  
**Etiquetas:** `unit-test`, `enhancement`, `test-double`, `coverage`, `report`

## Columnas

- **TO-DO:** tareas definidas y todavía no iniciadas.
- **CURRENT ITERATION:** tareas comprometidas para esta iteración.
- **IN PROGRESS:** tarea que se está ejecutando.
- **FIX VALIDATION:** tarea implementada pendiente de ejecutar pruebas, cobertura y revisión.
- **DONE:** tarea validada y respaldada con evidencia.

## Tarjetas

| ID local | Tarea / issue | Descripción y criterio de aceptación | Responsable | Etiqueta | Duración | Estado |
|---|---|---|---|---|---:|---|
| QUALITY-01 | Preparar entorno de pruebas | Confirmar `uv`, pytest, pytest-cov y dependencias del proyecto; separar pruebas de implementación. | Equipo | enhancement | 30 min | CURRENT ITERATION |
| QUALITY-02 | Pruebas unitarias del agregado Pago | Cubrir creación, invariantes, aprobación y rechazo con Arrange/Act/Assert. | Carlos Gutierrez Castilla | unit-test | 45 min | DONE |
| QUALITY-03 | Dobles para ServicioPagos | Aislar repositorios y unidad de trabajo con `Mock`/`create_autospec`; verificar llamadas y resultados. | Javier Peñalva | test-double | 60 min | DONE |
| QUALITY-04 | Validar casos negativos | Cubrir pedido inexistente, cliente no autorizado, monto distinto y pago duplicado. | Equipo | unit-test | 45 min | DONE |
| QUALITY-05 | Ejecutar pruebas y cobertura | Generar JUnit XML y `coverage.xml`; comprobar umbral de cobertura del módulo de pagos. | Equipo | coverage | 30 min | DONE |
| QUALITY-06 | Elaborar informe de ejecución | Registrar comando, fecha, versión, cantidad de pruebas, aprobadas/fallidas y conclusiones. | Equipo | report | 30 min | DONE |
| QUALITY-07 | Revisión final del flujo de calidad | Revisar código, evidencias, tablero y trazabilidad de commits/issues. | Equipo | enhancement | 20 min | DONE |
| QUALITY-08 | Automatizar ejecución de pruebas y reportes | Ejecutar pruebas, cobertura y reportes JUnit/XML con un único comando reproducible. | `carlosGCMP` | automation | 30 min | DONE |
| QUALITY-09 | Integrar validación automática en CI | Ejecutar `make quality` en un entorno limpio y conservar los reportes como artefactos. | `carlosGCMP`, `javierRock` | automation | 45 min | DONE |
| QUALITY-10 | Documentar ciclo TDD y refactorización | Registrar Red-Green-Refactor y la evidencia de las pruebas de dominio y servicio. | `carlosGCMP`, `javierRock` | tdd | 45 min | DONE |
| QUALITY-11 | Asociar commits con Issues | Mantener trazabilidad entre Issues, commits y archivos entregables del flujo de calidad. | Equipo | traceability | 20 min | DONE |
| QUALITY-12 | Completar evidencia final de automatización | Reunir capturas del tablero, consola, JUnit, cobertura, diagrama y explicación de `make quality`. | Equipo | documentation | 30 min | CURRENT ITERATION |

## Flujo de trabajo

1. Mover la tarjeta a **IN PROGRESS** antes de cambiar código.
2. Implementar el caso con Arrange/Act/Assert y el doble necesario.
3. Ejecutar las pruebas localmente.
4. Si falla, corregir y dejar la tarjeta en **FIX VALIDATION**.
5. Al pasar pruebas y cobertura, mover a **DONE** y conservar los reportes.
6. En GitHub, cada tarjeta debe convertirse en un Issue y vincularse al Project. El commit puede usar `fix #<número>` cuando exista el Issue remoto.

## Correspondencia con los objetivos

- Actividad 3: tablero con las cinco columnas y tarjetas con nombre, descripción, responsable, etiqueta y duración.
- Actividades 5 y 6: pruebas de dominio y servicio de aplicación usando dobles.
- Actividad 7: informe de ejecución y reporte de cobertura.

## Tablero GitHub publicado

- **Proyecto:** [SoftwareTextil — Quality & Automation](https://github.com/users/carlosGCMP/projects/1)
- **Rama:** [testing-automation](https://github.com/javierRock/SoftwareTextil/tree/testing-automation)
- **Issues:** [#8](https://github.com/javierRock/SoftwareTextil/issues/8), [#9](https://github.com/javierRock/SoftwareTextil/issues/9), [#10](https://github.com/javierRock/SoftwareTextil/issues/10), [#11](https://github.com/javierRock/SoftwareTextil/issues/11), [#12](https://github.com/javierRock/SoftwareTextil/issues/12), [#13](https://github.com/javierRock/SoftwareTextil/issues/13), [#14](https://github.com/javierRock/SoftwareTextil/issues/14), [#15](https://github.com/javierRock/SoftwareTextil/issues/15), [#16](https://github.com/javierRock/SoftwareTextil/issues/16), [#17](https://github.com/javierRock/SoftwareTextil/issues/17), [#18](https://github.com/javierRock/SoftwareTextil/issues/18), [#19](https://github.com/javierRock/SoftwareTextil/issues/19)

El proyecto está configurado como tablero y usa el campo `Status` con las columnas `TO-DO`, `CURRENT ITERATION`, `IN PROGRESS`, `FIX VALIDATION` y `DONE`. Las tarjetas #8–#18 están en `DONE`; #19 permanece en `CURRENT ITERATION` porque reúne las capturas y la presentación final.

## Contribuidores asignados

- `carlosGCMP`: entorno, informe y cobertura.
- `javierRock`: módulo de pagos, dominio y dobles.
- `Angel-Cs2004`: revisión final del equipo.
- `novato-intlgnt`: revisión final del equipo.
- `Lizzy354`: revisión final del equipo.
