# Organización de ramas

## Ramas activas

| Rama | Uso | Estado |
|---|---|---|
| `dev` | Integración del proyecto SoftwareTextil y trabajo general del equipo. | Activa y rama predeterminada del repositorio. |
| `testing-automation` | Pruebas unitarias, dobles, cobertura, Kanban y automatización. | Activa y publicada. |
| `build-automation` | Construcción reproducible y evidencias de Jenkins/Make. | Activa y publicada. |

## Convención para nuevos trabajos

- `feature/<modulo>-<responsable>` para una funcionalidad en desarrollo.
- `work/<tema>` para un bloque de trabajo aislado.
- `fix/<tema>` para una corrección puntual.
- Los nombres de ramas no deben incluir `codex`.

## Archivo histórico

Las ramas antiguas se conservan como tags `archive/*` antes de retirarse del listado de ramas activas. Esto mantiene disponibles sus commits y evita mezclar trabajo histórico con las entregas activas.

## Regla de integración

1. El trabajo nuevo parte de `dev` o de la rama de trabajo correspondiente.
2. Cada cambio se registra en una rama descriptiva.
3. La validación se ejecuta antes de integrar.
4. La rama `testing-automation` contiene las pruebas, validaciones y documentación de calidad del producto.
