# Tareas propuestas para @carlosGCMP

## Q-02 · Usuarios

- Separar las políticas de contraseñas y reloj de los servicios de aplicación.
- Etiqueta `code smell`. Prioridad media. Estimación 3 h.
- Ubicación `apps/usuarios/application/services.py:7`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## Q-03 · Usuarios

- Extraer creación y respuesta de sesión de login.
- Etiqueta `code smell`. Prioridad media. Estimación 2 h.
- Ubicación `apps/usuarios/application/services.py:48`. Estado **FIX VALIDATION**. Commit local `afc3b6d`.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## Q-04 · Usuarios

- Verificar rollback si falla el guardado de contraseña y delimitar la transacción.
- Etiqueta `code smell`. Prioridad alta. Estimación 3 h.
- Ubicación `apps/usuarios/application/services.py:134`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## Q-05 · Roles

- Guardar rol y permisos en una transacción.
- Etiqueta `bug`. Prioridad alta. Estimación 2 h.
- Ubicación `apps/usuarios/infrastructure/repositories.py:126`. Estado **FIX VALIDATION**. Commit local `afc3b6d`.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## S-04 · Compartido

- Validar dos alertas StrEnum con un analizador compatible.
- Etiqueta `code smell`. Prioridad media. Estimación 1 h.
- Ubicación `apps/compartido/infrastructure/campos.py:25`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## S-07 · Autenticación React

- Estabilizar el valor del contexto si el perfil de rendimiento lo justifica.
- Etiqueta `code smell`. Prioridad baja. Estimación 2 h.
- Ubicación `frontend/inventario/src/auth/AuthContext.jsx:71`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.

## S-09 · Autenticación estática

- Simplificar dos expresiones y revisar los consumidores del archivo.
- Etiqueta `code smell`. Prioridad baja. Estimación 2 h.
- Ubicación `static/usuarios/auth.js:113`. Estado **TO-DO**.
- Para cerrar, enlazar la prueba o verificación del comportamiento y el commit que resuelve la tarea.
