# Inventario inicial de calidad

Consulta la [matriz consolidada de la entrega actual](matriz.md) para ver el reparto y los resultados ampliados.

Base revisada: `a312d0a` de `origin/dev`. Origen de los siguientes hallazgos: revisión manual, no SonarQube.
Los responsables de equipo son propuestas pendientes de confirmación; Carlos es el responsable inicial del alcance de usuarios.

| ID | Tipo / categoría | Descripción y evidencia | Módulo o componente | Responsable | Prioridad | Estrategia | Estimación | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q-01 | Code smell / Clean Code, DRY | `_reservar` y `_liberar` repiten ordenamiento, búsqueda bloqueada, validación y persistencia; cambia la operación de stock | `apps/ventas/pedidos/application/services.py` | Por confirmar | Media | Extract Method para recorrido compartido conservando orden de bloqueos, errores y unidad de trabajo | 2 h | TO-DO |
| Q-02 | Code smell / SOLID, DIP | El servicio importa directamente hashers, validación y reloj de Django, dificultando probar políticas sin framework | `apps/usuarios/application/services.py` | carlosGCMP | Media | Extract Interface para política de contraseñas y reloj; adaptar infraestructura y mantener respuestas | 3 h | TO-DO |
| Q-03 | Code smell / Clean Code | `login` combina validación, auditoría, construcción de sesión y armado de respuesta | `apps/usuarios/application/services.py`, `ServicioAutenticacion.login` | carlosGCMP | Media | Extract Method para creación de sesión y respuesta; conservar contratos y auditoría | 2 h | TO-DO |
| Q-04 | Riesgo de consistencia / bug candidato | `crear_usuario` guarda usuario y contraseña por separado sin unidad de trabajo explícita; falta comprobar rollback si falla la segunda operación | `apps/usuarios/application/services.py`, `crear_usuario` | carlosGCMP | Alta | Prueba de fallo + unidad de trabajo inyectada con adaptador transaccional; confirmar antes de declarar bug | 3 h | TO-DO |
| Q-05 | Riesgo de consistencia / bug candidato | Guardar un rol y sincronizar permisos involucra varias escrituras sin atomicidad explícita dentro del repositorio | `apps/usuarios/infrastructure/repositories.py`, `DjangoRepositorioRol.guardar` | carlosGCMP | Alta | Prueba de rollback y delimitación transaccional de la operación | 2 h | TO-DO |

## Hallazgos SonarQube y ejecución local

Q-01, Q-03 y Q-05 fueron implementados y pasan pruebas; están en FIX VALIDATION para revisión del usuario. Q-05 quedó confirmado como bug por dos fallos reproducibles antes del cambio.

| ID | Regla / origen | Componente | Responsable local | Prioridad | Estrategia y estado |
| --- | --- | --- | --- | --- | --- |
| S-01 | css:S4656 | `apps/inventario/index.html`, `.skeleton-bar` | carlosGCMP | Baja | Cambiar el fallback a `background-color` conservando gradiente; FIX VALIDATION |
| S-02 | python:S1192 | `apps/ventas/models.py` | carlosGCMP | Baja | Extract Constant para referencia al modelo de usuario; FIX VALIDATION |
| S-03 | python:S1192 | `config/urls.py` | carlosGCMP | Baja | Extract Constant para prefijo de rutas de ventas; FIX VALIDATION |
| S-04 | python:S5864, dos ubicaciones | `apps/compartido/infrastructure/campos.py` | Pendiente | Media | Revisar posible falso positivo: el scanner 9.9.7 no soporta explícitamente Python 3.11 y analiza como 3.10; `StrEnum` sí es iterable en el runtime. No alterar el dominio para ocultar la alerta |
| S-05 | python:S2208, tres ubicaciones | `config/settings/{dev,prod,build}.py` | Pendiente | Baja | Evaluar importación de configuración Django por ambiente; siguen abiertos, sin supresión |

Los ocho issues originales completos, con regla, mensaje, severidad y ubicación, se conservan en `evidencias/antes/sonarqube/issues.json`. La matriz combina esta fuente con los cinco hallazgos manuales.

## Reglas de consolidación

- Añadir ubicación exacta y enlace del issue al publicar cada tarea.
- Incorporar hallazgos SonarQube con su regla e identificador originales.
- Verificar contexto de despliegue antes de clasificar configuración de desarrollo como vulnerabilidad.
- Un riesgo observado no es un bug demostrado hasta reproducirlo; las estrategias se validan mediante pruebas.
- No asignar trabajo como completado ni atribuir commits a otros integrantes sin evidencia.
