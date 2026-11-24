# Tareas propuestas para @javierRock

## Q-10 · Despachos

- Aislar confirmación y descuento de reservas conservando la transacción.
- Etiqueta `code smell`. Prioridad media. Estimación 3 h.
- Ubicación `apps/ventas/despachos/application/services.py:88`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## Q-11 · Pagos

- Expresar consultas normales y con bloqueo mediante operaciones explícitas.
- Etiqueta `code smell`. Prioridad baja. Estimación 2 h.
- Ubicación `apps/ventas/pagos/application/services.py:121`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## A-01 · GitHub Actions

- Incluir refactor/** en los eventos push de CI.
- Etiqueta `enhancement`. Prioridad media. Estimación 1 h.
- Ubicación `.github/workflows/ci.yml:5`. Estado **FIX VALIDATION**. Commit local `7d490ce`.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## A-02 · Make

- Exigir Node 22.12+ para la serie 22 y mantener la serie 20 compatible.
- Etiqueta `bug`. Prioridad media. Estimación 1 h.
- Ubicación `Makefile:24`. Estado **FIX VALIDATION**. Commit local `7d490ce`.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## A-03 · Jenkins

- Reutilizar las validaciones y el empaquetado ya ejecutados luego de consolidar los reportes.
- Etiqueta `enhancement`. Prioridad media. Estimación 2 h.
- Ubicación `Jenkinsfile:45`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## A-04 · Construcción

- Priorizar los 58 diagnósticos Ruff que impiden superar la revisión estricta de Make.
- Etiqueta `enhancement`. Prioridad alta. Estimación 3 h.
- Ubicación `Makefile:50`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## S-05 · Configuración Django

- Revisar tres imports de configuración y verificar ambientes antes de ajustarlos.
- Etiqueta `code smell`. Prioridad baja. Estimación 2 h.
- Ubicación `config/settings/dev.py:9`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.
