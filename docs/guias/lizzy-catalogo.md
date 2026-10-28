# Guía de Trabajo — Lizzy · Catálogo

- **Integrante:** Huayhua Perez, Lizzy Arlette
- **Rama:** `feature/catalogo-lizzy`
- **Módulo:** `apps/catalogo` (prendas, categorías, tipos de producto)

## 1. Alcance y archivos del módulo

| Capa | Archivos |
| --- | --- |
| Dominio | `apps/catalogo/domain/prenda.py`, `apps/catalogo/domain/repositorios.py` |
| Aplicación | `apps/catalogo/application/services.py` |
| Infraestructura | `apps/catalogo/models.py`, `apps/catalogo/infrastructure/models.py`, `apps/catalogo/infrastructure/repositories.py` |
| Presentación | `apps/catalogo/presentation/serializers.py`, `views.py`, `urls.py` |

## 2. Estilo de programación (a declarar)

> **Estilo elegido:** _(completa aquí: nombre del estilo, distinto al del resto del equipo — ver lista en [README.md](README.md))_
>
> **Descripción de cómo lo aplicas en tu módulo:** _(2–4 líneas)_
>
> **Evidencia (fragmento de código con ruta y líneas):**
>
> ```python
> # apps/catalogo/...
> ```

Sugerencia natural para este módulo: **Pipeline** — el listado/búsqueda de prendas como cadena de funciones puras (filtrar por categoría → filtrar por estado → mapear a DTO), sin estado compartido.

## 3. Objetivos de refactor con SOLID (evidencia 3+)

| # | Problema actual | Refactor | Principio |
| --- | --- | --- | --- |
| 1 | `ServicioCatalogo` instancia/recibe repositorios concretos `Django*` (`application/services.py`) | Tipar e inyectar los ABCs de `domain/repositorios.py` | **DIP** |
| 2 | Los repositorios concretos no heredan los contratos ABC (`infrastructure/repositories.py`) | `class DjangoRepositorioPrenda(RepositorioPrenda)` y equivalentes | **LSP** |
| 3 | `PrendaViewSet`, `CategoriaViewSet`, `TipoProductoViewSet` usan `queryset` + `ModelSerializer` directo | Todas las acciones pasan por `ServicioCatalogo`; las views solo serializan | **SRP** |
| 4 | Contratos de repositorio: verificar que cada agregado tenga su contrato pequeño y específico (Prenda / Categoria / TipoProducto separados) | Mantener interfaces mínimas por agregado, sin métodos que nadie usa | **ISP** |

## 4. Prácticas de Clean Code (evidencia 5+)

| # | Práctica | Dónde la aplicaste | Fragmento (ruta:líneas) |
| --- | --- | --- | --- |
| 1 | Nombres significativos (lenguaje ubicuo: `Prenda`, `cambiar_precio`, `EstadoPrenda`) | | |
| 2 | Funciones pequeñas, una sola responsabilidad | | |
| 3 | Sin valores mágicos (estados y monedas como enums/constantes, no strings sueltos) | | |
| 4 | Manejo de errores explícito (p. ej. `PrecioInvalido` si el precio es negativo, `PrendaNoEncontrada`) | | |
| 5 | DRY (conversión modelo↔entidad centralizada en mappers reutilizados) | | |

## 5. Mapa DDD del módulo (evidencia para la rúbrica)

| Elemento DDD | Clase(s) | Archivo |
| --- | --- | --- |
| Entidades | `Prenda`, `Categoria`, `TipoProducto` | `apps/catalogo/domain/prenda.py` |
| Objetos de Valor | `Dinero` (precio de la prenda), `EstadoPrenda` | `apps/compartido/domain/dinero.py`, `apps/compartido/domain/enums.py` |
| Agregado | `Prenda` (raíz, con precio `Dinero` y estado; métodos `activar`, `desactivar`, `cambiar_precio`) | `apps/catalogo/domain/prenda.py` |
| Fábrica | `PrendaFabrica` | `apps/catalogo/domain/prenda.py` |
| Repositorios (contratos) | `RepositorioPrenda`, `RepositorioCategoria`, `RepositorioTipoProducto` | `apps/catalogo/domain/repositorios.py` |
| Repositorios (implementación) | `DjangoRepositorioPrenda` y equivalentes | `apps/catalogo/infrastructure/repositories.py` |
| Servicio | `ServicioCatalogo` | `apps/catalogo/application/services.py` |
| Módulo | App `catalogo` con 4 capas | `apps/catalogo/` |

## 6. Definición de hecho

- [ ] Estilo de programación declarado y evidenciado (sección 2).
- [ ] Los 4 refactors SOLID implementados y evidenciados (sección 3).
- [ ] 5+ prácticas Clean Code evidenciadas (sección 4).
- [ ] CRUD de prendas, categorías y tipos funciona (`uv run python manage.py check` + prueba manual de la API `api/prendas/`).
- [ ] Commits solo dentro de `apps/catalogo`.
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).
