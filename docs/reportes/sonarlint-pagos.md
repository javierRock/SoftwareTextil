# Reporte SonarLint - Módulo de Pagos

## Alcance

Archivos que deben analizarse en SonarQube for IDE/SonarLint:

- `apps/ventas/pagos/**/*.py`
- `apps/ventas/models.py`, limitado a `PagoModel` y a la limpieza de imports compartidos
- `apps/ventas/migrations/0002_integridad_pago.py`
- `apps/usuarios/presentation/authentication.py`, limitado al encabezado Bearer
- `tests/pagos/**/*.py`

## Estado verificable

SonarLint/SonarQube for IDE no se ejecutó en esta sesión. No existe `sonar-scanner` en `PATH` y el entorno no expone resultados ni la interfaz del IDE. En consecuencia, este documento no atribuye reglas, severidades ni conteos a Sonar.

Sí se ejecutó análisis estático independiente con Ruff:

```bash
uv run ruff check apps/ventas/pagos tests/pagos apps/ventas/models.py apps/ventas/migrations/0002_integridad_pago.py
uv run ruff format --check apps/ventas/pagos tests/pagos apps/ventas/models.py apps/ventas/migrations/0002_integridad_pago.py
```

Ruff reportó `All checks passed!`; el formato se aplicó a los tres archivos que la primera revisión marcó. Ruff no sustituye el análisis de seguridad y mantenibilidad de SonarLint.

## Correcciones de revisión local

Estos hallazgos proceden de revisión manual y Ruff, no de SonarLint:

| Hallazgo | Severidad Sonar | Archivo | Corrección | Estado |
| --- | --- | --- | --- | --- |
| Reexportación mediante `import *` y `# noqa` | No atribuida | `infrastructure/models.py` | Import explícito de `PagoModel` y `__all__` | Corregido |
| Acceso directo al ORM desde presentación | No atribuida | `presentation/views.py` | Todas las operaciones pasan por `ServicioPagos` | Corregido |
| Errores de dominio expresados como `ValueError` | No atribuida | `domain/pago.py`, `application/services.py` | Jerarquía `ErrorPago` y traducción HTTP centralizada | Corregido |
| Dependencia del servicio sobre el repositorio Django | No atribuida | `application/services.py` | Inyección de `RepositorioPago` | Corregido |
| Posible recepción de número de tarjeta, CVV o PIN | No atribuida | `presentation/serializers.py` | Rechazo explícito de campos sensibles | Corregido |
| Consultas sin orden definido | No atribuida | `infrastructure/repositories.py` | Orden por `fecha` e `id` | Corregido |
| API anónima y sin control de propiedad | No atribuida | `presentation/views.py` | Token Bearer, permisos por rol y validación del dueño | Corregido |
| Carrera entre aprobar y rechazar | No atribuida | `application/services.py` | Unidad de trabajo, transacción y bloqueo de filas | Corregido |
| Pago desconectado de Pedido | No atribuida | `application/ports.py`, `infrastructure/pedidos.py` | Puerto anticorrupción y actualización atómica | Corregido |
| Listado sin límites | No atribuida | `presentation/serializers.py`, `domain/repositorios.py` | Paginación con máximo de 100 | Corregido |
| Integridad solo en memoria | No atribuida | `apps/ventas/models.py` | Restricciones e índice mediante migración | Corregido |

## Registro de SonarLint

La tabla queda preparada para registrar únicamente resultados reales del IDE:

| Regla | Severidad | Archivo y línea | Corrección | Estado |
| --- | --- | --- | --- | --- |
| Sin resultados registrados | No determinada | No aplica | Ejecutar análisis manual | Pendiente |

## Pasos manuales pendientes

1. Abrir el repositorio en un IDE con SonarQube for IDE/SonarLint instalado.
2. Analizar los archivos definidos en el alcance.
3. Registrar en la tabla la regla exacta, severidad, ubicación y corrección.
4. Corregir primero cualquier hallazgo Blocker o Critical y volver a analizar.
5. Revisar los Major razonables sin silenciar reglas de forma injustificada.
6. Adjuntar capturas donde se vean fecha, archivo, regla y estado final.

## Evidencia gráfica

No se adjuntaron capturas porque SonarLint no pudo ejecutarse desde este entorno. Las capturas reales del IDE deben añadirse después del análisis manual; no se incluyen imágenes simuladas ni resultados inventados.
