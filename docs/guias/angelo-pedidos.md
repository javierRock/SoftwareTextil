# Guía de Trabajo — Angelo · Pedidos

- **Integrante:** Quispe Suarez, Angelo Josué
- **Rama:** `feature/pedidos-angelo`
- **Módulo:** `apps/ventas/pedidos` (y su origen: `apps/ventas/carrito`)

## 1. Alcance y archivos del módulo

| Capa | Archivos |
| --- | --- |
| Dominio | `apps/ventas/pedidos/domain/pedido.py`, `apps/ventas/pedidos/domain/repositorios.py`, `apps/ventas/carrito/domain/carrito.py` |
| Aplicación | `apps/ventas/pedidos/application/services.py`, `apps/ventas/carrito/application/services.py` |
| Infraestructura | `apps/ventas/models.py` (compartido con pagos — coordinar con Javier), `apps/ventas/pedidos/infrastructure/repositories.py` |
| Presentación | `apps/ventas/pedidos/presentation/serializers.py`, `views.py`, `urls.py` |

## 2. Estilo de programación (a declarar)

> **Estilo elegido:** _(completa aquí: nombre del estilo, distinto al del resto del equipo — ver lista en [README.md](README.md))_
>
> **Descripción de cómo lo aplicas en tu módulo:** _(2–4 líneas)_
>
> **Evidencia (fragmento de código con ruta y líneas):**
>
> ```python
> # apps/ventas/pedidos/...
> ```

Sugerencia natural para este módulo: **Cookbook** — `generar_desde_carrito` como receta con pasos nombrados (validar carrito → construir detalles → calcular total → persistir → marcar carrito convertido).

## 3. Objetivos de refactor con SOLID (evidencia 3+)

| # | Problema actual | Refactor | Principio |
| --- | --- | --- | --- |
| 1 | `ServicioPedidos` depende de repositorios concretos, incluido el del carrito (`pedidos/application/services.py`) | Tipar e inyectar los ABCs de `pedidos/domain/repositorios.py` y `carrito/domain/repositorios.py` | **DIP** |
| 2 | Los repositorios concretos no heredan los contratos ABC (`pedidos/infrastructure/repositories.py`) | `class DjangoRepositorioPedido(RepositorioPedido)` y equivalentes | **LSP** |
| 3 | `PedidoViewSet` usa `queryset` + `ModelSerializer` directo en varias acciones | Todas las acciones pasan por `ServicioPedidos`; las views solo serializan | **SRP** |
| 4 | `apps/ventas/models.py` concentra los modelos de carrito, pedidos **y** pagos en un solo archivo (Módulos DDD débiles) | Junto con Javier: separar los modelos por submódulo (o documentar por qué se quedan juntos por las migraciones) | **SRP / Módulos** |

## 4. Prácticas de Clean Code (evidencia 5+)

| # | Práctica | Dónde la aplicaste | Fragmento (ruta:líneas) |
| --- | --- | --- | --- |
| 1 | Nombres significativos (lenguaje ubicuo: `Pedido`, `generar_desde_carrito`, `marcar_pagado`) | | |
| 2 | Funciones pequeñas, una sola responsabilidad (descomponer `generar_desde_carrito` en pasos) | | |
| 3 | Sin valores mágicos (estados de pedido solo vía `EstadoPedido`, nunca strings sueltos) | | |
| 4 | Manejo de errores explícito (p. ej. `CarritoVacio`, `PedidoNoCancelable` como excepciones de dominio) | | |
| 5 | DRY (cálculo de totales en un solo lugar: el agregado, no repetido en serializers/servicios) | | |

## 5. Mapa DDD del módulo (evidencia para la rúbrica)

| Elemento DDD | Clase(s) | Archivo |
| --- | --- | --- |
| Entidades | `DetallePedido`, `ItemCarrito` | `apps/ventas/pedidos/domain/pedido.py`, `apps/ventas/carrito/domain/carrito.py` |
| Objetos de Valor | `Dinero` (total del pedido), `EstadoPedido`, `EstadoCarrito` | `apps/compartido/domain/dinero.py`, `apps/compartido/domain/enums.py` |
| Agregados | `Pedido` (raíz con sus detalles), `CarritoCompras` (raíz con sus items) | `apps/ventas/pedidos/domain/pedido.py`, `apps/ventas/carrito/domain/carrito.py` |
| Fábricas | `PedidoFactory`, `CarritoFactory` | `apps/ventas/pedidos/domain/pedido.py`, `apps/ventas/carrito/domain/carrito.py` |
| Repositorios (contratos) | `RepositorioPedido`, `RepositorioCarrito` | `apps/ventas/pedidos/domain/repositorios.py`, `apps/ventas/carrito/domain/repositorios.py` |
| Repositorios (implementación) | `DjangoRepositorioPedido` y equivalentes | `apps/ventas/pedidos/infrastructure/repositories.py` |
| Servicios | `ServicioPedidos`, `ServicioCompras` | `apps/ventas/pedidos/application/services.py`, `apps/ventas/carrito/application/services.py` |
| Módulo | Submódulos `pedidos` y `carrito` con 4 capas | `apps/ventas/pedidos/`, `apps/ventas/carrito/` |

## 6. Definición de hecho

- [ ] Estilo de programación declarado y evidenciado (sección 2).
- [ ] Los 4 refactors SOLID implementados y evidenciados (sección 3).
- [ ] 5+ prácticas Clean Code evidenciadas (sección 4).
- [ ] Flujo carrito → pedido → cancelar/consultar funciona (`uv run python manage.py check` + prueba manual de `api/ventas/pedidos/`).
- [ ] Commits solo dentro de `apps/ventas/pedidos` y `apps/ventas/carrito` (+ `apps/ventas/models.py` coordinado con Javier).
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).
