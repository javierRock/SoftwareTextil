# Flujo de Trabajo Git — Proyecto Final

Flujo de ramas exigido por el proyecto final: `master/main`, `dev` (desarrollo) y una rama `feature` por funcionalidad a evolucionar.

## Ramas

```text
main                          # Releases estables (solo merges desde dev)
└── dev                       # Integración del equipo
    ├── feature/autenticacion-carlos
    ├── feature/catalogo-lizzy
    ├── feature/inventario-alejandro
    ├── feature/pedidos-angelo
    └── feature/pagos-javier
```

| Rama | Propósito | Quién escribe |
| --- | --- | --- |
| `main` | Versión estable presentable | Solo merges desde `dev` |
| `dev` | Integración continua del equipo | Solo merges por Pull Request |
| `feature/<modulo>-<integrante>` | Desarrollo de un módulo | El integrante dueño del módulo |

## Ciclo de trabajo de cada integrante

1. **Situarse en su rama**:

   ```bash
   git checkout feature/<modulo>-<integrante>
   ```

2. **Trabajar en su módulo** siguiendo su guía en `docs/guias/`, con commits pequeños y frecuentes (cada commit cuenta como evidencia de participación).

3. **Sincronizar con `dev`** antes de abrir el PR (rebase o merge, según acuerde el equipo):

   ```bash
   git fetch origin
   git rebase origin/dev        # o: git merge origin/dev
   ```

4. **Publicar y abrir Pull Request** hacia `dev`:

   ```bash
   git push origin feature/<modulo>-<integrante>
   ```

   El PR debe ser revisado y aprobado por al menos otro integrante antes del merge. **No borrar la rama feature después del merge** (es evidencia para la evaluación).

5. **Release**: cuando `dev` esté estable, el equipo abre un PR `dev → main`.

## Convención de commits

Formato: `<tipo>: <descripción en español, en infinitivo>`

| Tipo | Uso |
| --- | --- |
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug o defecto |
| `refactor` | Refactorización (smells, Clean Code, SOLID) sin cambiar comportamiento |
| `test` | Agregar o corregir pruebas |
| `docs` | Documentación (README, guías, diagramas) |

Ejemplos:

```text
feat: registrar pago con metodo de pago y referencia
refactor: inyectar contrato de repositorio en ServicioPagos (DIP)
docs: declarar estilo de programacion del modulo pagos
```

## Reglas del equipo

- Nunca hacer commits directos a `dev` ni a `main`.
- Cada integrante hace commits **solo** dentro de su módulo asignado; los cambios compartidos (`apps/compartido`, `config/`) se coordinan antes en el grupo.
- Cada PR debe indicar en su descripción qué evidencia aporta: estilo aplicado, prácticas Clean Code y principios SOLID (con enlace a su guía).
- Resolver conflictos siempre en la rama feature (tras rebase/merge de `dev`), nunca en `dev`.
