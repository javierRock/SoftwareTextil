# Guía de Trabajo — Javier · Pagos

- **Integrante:** Peñalva Humire, Javier Alonzo
- **Rama:** `feature/pagos-javier`
- **Módulo:** `apps/ventas/pagos` (registro, aprobación y rechazo de pagos)

## 1. Alcance y archivos del módulo

| Capa | Archivos |
| --- | --- |
| Dominio | `apps/ventas/pagos/domain/pago.py`, `apps/ventas/pagos/domain/repositorios.py` |
| Aplicación | `apps/ventas/pagos/application/services.py` |
| Infraestructura | `apps/ventas/models.py` (compartido con pedidos — coordinar con Angelo), `apps/ventas/pagos/infrastructure/repositories.py` |
| Presentación | `apps/ventas/pagos/presentation/serializers.py`, `views.py`, `urls.py` |

## 2. Estilo de programación (a declarar)

> **Estilo elegido:** _(completa aquí: nombre del estilo, distinto al del resto del equipo — ver lista en [README.md](README.md))_
>
> **Descripción de cómo lo aplicas en tu módulo:** _(2–4 líneas)_
>
> **Evidencia (fragmento de código con ruta y líneas):**
>
> ```python
> # apps/ventas/pagos/...
> ```

Sugerencia natural para este módulo: un estilo de **manejo de errores** (**Tantrum**: un pago inválido falla inmediato con excepción específica; o **Passive-Aggressive**: las excepciones de dominio suben hasta la view, único punto que responde HTTP) — o **RESTful**, modelando el pago como recurso con transiciones de estado.

## 3. Objetivos de refactor con SOLID (evidencia 3+)

| # | Problema actual | Refactor | Principio |
| --- | --- | --- | --- |
| 1 | `ServicioPagos` depende de repositorios concretos `Django*` (`pagos/application/services.py`) | Tipar e inyectar el ABC `RepositorioPago` de `domain/repositorios.py` | **DIP** |
| 2 | Los repositorios concretos no heredan los contratos ABC (`pagos/infrastructure/repositories.py`) | `class DjangoRepositorioPago(RepositorioPago)` | **LSP** |
| 3 | `PagoViewSet` usa `queryset` + `ModelSerializer` directo en varias acciones | Todas las acciones pasan por `ServicioPagos`; las views solo serializan | **SRP** |
| 4 | Métodos de pago (`MetodoPago`) tratados con condicionales; agregar uno nuevo obliga a tocar el servicio | Estrategia por método de pago (una clase por método que valida/procesa); nuevos métodos = nuevas clases | **OCP** |

## 4. Prácticas de Clean Code (evidencia 5+)

| # | Práctica | Dónde la aplicaste | Fragmento (ruta:líneas) |
| --- | --- | --- | --- |
| 1 | Nombres significativos (lenguaje ubicuo: `Pago`, `aprobar`, `rechazar`, `MetodoPago`) | | |
| 2 | Funciones pequeñas, una sola responsabilidad | | |
| 3 | Sin valores mágicos (estados y métodos de pago solo vía enums de `apps/compartido/domain/enums.py`) | | |
| 4 | Manejo de errores explícito (p. ej. `PagoYaProcesado`, `MontoInvalido` como excepciones de dominio) | | |
| 5 | Comentarios solo donde aportan (las transiciones `aprobar`/`rechazar` se explican solas) | | |

## 5. Mapa DDD del módulo (evidencia para la rúbrica)

| Elemento DDD | Clase(s) | Archivo |
| --- | --- | --- |
| Entidad / Agregado | `Pago` (raíz; transiciones `aprobar`/`rechazar` con invariantes de estado) | `apps/ventas/pagos/domain/pago.py` |
| Objetos de Valor | `Dinero` (monto), `EstadoPago`, `MetodoPago` | `apps/compartido/domain/dinero.py`, `apps/compartido/domain/enums.py` |
| Fábrica | `PagoFactory` | `apps/ventas/pagos/domain/pago.py` |
| Repositorio (contrato) | `RepositorioPago` | `apps/ventas/pagos/domain/repositorios.py` |
| Repositorio (implementación) | `DjangoRepositorioPago` | `apps/ventas/pagos/infrastructure/repositories.py` |
| Servicio | `ServicioPagos` | `apps/ventas/pagos/application/services.py` |
| Módulo | Submódulo `pagos` con 4 capas | `apps/ventas/pagos/` |

## 6. Definición de hecho

- [ ] Estilo de programación declarado y evidenciado (sección 2).
- [ ] Los 4 refactors SOLID implementados y evidenciados (sección 3).
- [ ] 5+ prácticas Clean Code evidenciadas (sección 4).
- [ ] Registrar/aprobar/rechazar pago y listar por pedido funciona (`uv run python manage.py check` + prueba manual de `api/ventas/pagos/`).
- [ ] Commits solo dentro de `apps/ventas/pagos` (+ `apps/ventas/models.py` coordinado con Angelo).
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).
