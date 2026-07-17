# Guía de Trabajo — Alejandro · Inventario

- **Integrante:** Condori Pallardel, Alejandro
- **Rama:** `feature/inventario-alejandro`
- **Módulo:** `apps/inventario` (stock, movimientos, alertas)

## 1. Alcance y archivos del módulo

| Capa | Archivos |
| --- | --- |
| Dominio | `apps/inventario/domain/stock_prenda.py`, `apps/inventario/domain/repositorios.py` |
| Aplicación | `apps/inventario/application/services.py` |
| Infraestructura | `apps/inventario/models.py`, `apps/inventario/infrastructure/models.py`, `apps/inventario/infrastructure/repositories.py` |
| Presentación | `apps/inventario/presentation/serializers.py`, `views.py`, `urls.py` |

## 2. Estilo de programación (a declarar)

> **Estilo elegido:** _(completa aquí: nombre del estilo, distinto al del resto del equipo — ver lista en [README.md](README.md))_
>
> **Descripción de cómo lo aplicas en tu módulo:** _(2–4 líneas)_
>
> **Evidencia (fragmento de código con ruta y líneas):**
>
> ```python
> # apps/inventario/...
> ```

Sugerencia natural para este módulo: **Declared Intentions** — type hints estrictos y validación declarada de invariantes (el VO `Stock` ya es `frozen` y no-negativo: extender ese enfoque a todo el módulo) — o **Persistent Tables**, apoyándote en consultas sobre `movimientos_inventario`.

## 3. Objetivos de refactor con SOLID (evidencia 3+)

| # | Problema actual | Refactor | Principio |
| --- | --- | --- | --- |
| 1 | `ServicioInventario` depende de repositorios concretos `Django*` (`application/services.py`) | Tipar e inyectar los ABCs de `domain/repositorios.py` | **DIP** |
| 2 | Los repositorios concretos no heredan los contratos ABC (`infrastructure/repositories.py`) | `class DjangoRepositorioStock(RepositorioStock)` y equivalentes | **LSP** |
| 3 | `StockViewSet`/`MovimientoViewSet` usan `queryset` + `ModelSerializer` directo en varias acciones | Todas las acciones pasan por `ServicioInventario`; las views solo serializan | **SRP** |
| 4 | Tipos de movimiento (ingreso/salida/ajuste) resueltos con condicionales en el servicio | Nuevos tipos de movimiento como nuevas clases/estrategias sin modificar `registrar_ingreso`/`registrar_salida` existentes | **OCP** |

## 4. Prácticas de Clean Code (evidencia 5+)

| # | Práctica | Dónde la aplicaste | Fragmento (ruta:líneas) |
| --- | --- | --- | --- |
| 1 | Nombres significativos (lenguaje ubicuo: `StockPrenda`, `registrar_ingreso`, `esta_bajo_minimo`) | | |
| 2 | Funciones pequeñas, una sola responsabilidad | | |
| 3 | Sin valores mágicos (nivel mínimo, unidades y estados de alerta como constantes/enums) | | |
| 4 | Manejo de errores explícito (p. ej. `StockInsuficiente` al registrar una salida mayor al disponible) | | |
| 5 | Evitar efectos ocultos (la generación de alertas es explícita: `generar_alerta_si_corresponde`) | | |

## 5. Mapa DDD del módulo (evidencia para la rúbrica)

| Elemento DDD | Clase(s) | Archivo |
| --- | --- | --- |
| Entidades | `MovimientoInventario`, `AlertaStock`, `MermaDefecto` | `apps/inventario/domain/stock_prenda.py` |
| Objeto de Valor | `Stock` (inmutable, no-negativo) | `apps/inventario/domain/stock_prenda.py` |
| Agregado | `StockPrenda` (raíz; invariantes de ingreso/salida/ajuste y alertas) | `apps/inventario/domain/stock_prenda.py` |
| Fábrica | `InventarioFabrica` | `apps/inventario/domain/stock_prenda.py` |
| Repositorios (contratos) | `RepositorioStock`, `RepositorioMovimiento`, `RepositorioAlerta` | `apps/inventario/domain/repositorios.py` |
| Repositorios (implementación) | `DjangoRepositorioStock` y equivalentes | `apps/inventario/infrastructure/repositories.py` |
| Servicio | `ServicioInventario` | `apps/inventario/application/services.py` |
| Módulo | App `inventario` con 4 capas | `apps/inventario/` |

## 6. Definición de hecho

- [ ] Estilo de programación declarado y evidenciado (sección 2).
- [ ] Los 4 refactors SOLID implementados y evidenciados (sección 3).
- [ ] 5+ prácticas Clean Code evidenciadas (sección 4).
- [ ] Consulta de stock, ingresos, salidas y alertas funcionan (`uv run python manage.py check` + prueba manual de `api/stock/`).
- [ ] Commits solo dentro de `apps/inventario`.
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).
