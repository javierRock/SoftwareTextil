# Organización de ramas

## Ramas activas

| Rama | Uso | Estado |
|---|---|---|
| `dev` | Integración del proyecto SoftwareTextil y trabajo general del equipo. | Activa y rama predeterminada del repositorio. |
| `laboratorio-05` | Entrega aislada del Laboratorio 05: pruebas unitarias, dobles, cobertura, Kanban y automatización. | Activa y publicada. |
| `lab03-automatic-build` | Entrega de la práctica de construcción automática y evidencias de Jenkins/Make. | Activa para conservar la práctica anterior. |

## Convención para nuevos trabajos

- `feature/<modulo>-<responsable>` para una funcionalidad en desarrollo.
- `lab/<numero>-<tema>` para una entrega académica aislada.
- `fix/<tema>` para una corrección puntual.
- Los nombres de ramas no deben incluir `codex`.

## Archivo histórico

Las ramas antiguas se conservan como tags `archive/*` antes de retirarse del listado de ramas activas. Esto mantiene disponibles sus commits y evita mezclar prácticas anteriores con la entrega del Laboratorio 05.

## Regla de integración

1. El trabajo nuevo parte de `dev` o de la rama del laboratorio correspondiente.
2. Cada cambio se registra en una rama descriptiva.
3. La validación se ejecuta antes de integrar.
4. La rama `laboratorio-05` solo contiene la evidencia y la implementación solicitada por el Laboratorio 05.
