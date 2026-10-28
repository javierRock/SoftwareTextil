# Guía de Trabajo — Alejandro · Inventario

- **Integrante:** Condori Pallardel, Alejandro
- **Rama:** `feature/inventario-alejandro`
- **Módulo:** `apps/inventario` (stock, movimientos, alertas)

## 1. Alcance y archivos del módulo

| Capa            | Archivos                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Dominio         | `apps/inventario/domain/stock_prenda.py`, `apps/inventario/domain/repositorios.py`                                        |
| Aplicación      | `apps/inventario/application/services.py`                                                                                 |
| Infraestructura | `apps/inventario/models.py`, `apps/inventario/infrastructure/models.py`, `apps/inventario/infrastructure/repositories.py` |
| Presentación    | `apps/inventario/presentation/serializers.py`, `views.py`, `urls.py`                                                      |

## 2. Estilo de programación

> **Estilo elegido:** **Declared Intentions**
>
> **Descripción de como se aplica en los módulos:**
> En inventario dejo las reglas visibles en los tipos, los nombres y las excepciones específicas. Los serializers solo parsean datos de entrada y el dominio decide si una cantidad o un stock son válidos. Así el flujo se lee como una intención explícita: validar, bloquear, modificar y guardar.
>
> **Evidencia (fragmento de código con ruta y líneas):**
>
> ```python
> # apps/inventario/domain/stock_prenda.py:63-83
> def registrar_ingreso(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
>     self._validar_cantidad(cantidad)
>     self.cantidad_actual += cantidad
>     self.ultima_actualizacion = datetime.utcnow()
>     return self._crear_movimiento(TipoMovimiento.INGRESO, cantidad, motivo, usuario_id)
>
> def registrar_salida(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
>     self._validar_cantidad(cantidad)
>     if cantidad > self.cantidad_actual:
>         raise StockInsuficiente("No hay stock suficiente para la salida")
>     self.cantidad_actual -= cantidad
>     self.ultima_actualizacion = datetime.utcnow()
>     return self._crear_movimiento(TipoMovimiento.SALIDA, cantidad, motivo, usuario_id)
> ```

Sugerencia natural para este módulo: **Declared Intentions** — type hints estrictos y validación declarada de invariantes (el VO `Stock` ya es `frozen` y no-negativo: extender ese enfoque a todo el módulo) — o **Persistent Tables**, apoyándote en consultas sobre `movimientos_inventario`.

## 3. Objetivos de refactor con SOLID

| #   | Problema actual                                                                                   | Refactor                                                                                                                  | Principio |
| --- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1   | `ServicioInventario` depende de repositorios concretos `Django*` (`application/services.py`)      | Tipar e inyectar los ABCs de `domain/repositorios.py`                                                                     | **DIP**   |
| 2   | Los repositorios concretos no heredan los contratos ABC (`infrastructure/repositories.py`)        | `class DjangoRepositorioStock(RepositorioStock)` y equivalentes                                                           | **LSP**   |
| 3   | `StockViewSet`/`MovimientoViewSet` usan `queryset` + `ModelSerializer` directo en varias acciones | Todas las acciones pasan por `ServicioInventario`; las views solo serializan                                              | **SRP**   |
| 4   | Tipos de movimiento (ingreso/salida/ajuste) resueltos con condicionales en el servicio            | Nuevos tipos de movimiento como nuevas clases/estrategias sin modificar `registrar_ingreso`/`registrar_salida` existentes | **OCP**   |

## 4. Prácticas de Clean Code

| #   | Práctica                                                                                         | Dónde la aplicaste                                   | Fragmento (ruta:líneas)                         |
| --- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------- | ----------------------------------------------- |
| 1   | Nombres significativos (lenguaje ubicuo: `StockPrenda`, `registrar_ingreso`, `esta_bajo_minimo`) | Dominio de inventario                                | `apps/inventario/domain/stock_prenda.py:53-86`  |
| 2   | Funciones pequeñas, una sola responsabilidad                                                     | Servicio y viewset delegan; el dominio decide reglas | `apps/inventario/application/services.py:40-65` |
| 3   | Sin valores mágicos (unidades, estados y tipo de movimiento con enums/defaults)                  | Tipos compartidos                                    | `apps/compartido/domain/enums.py:6-79`          |
| 4   | Manejo de errores explícito (excepciones de dominio: `CantidadInvalida`, `StockInsuficiente`)    | Reglas de negocio                                    | `apps/inventario/domain/excepciones.py:4-23`    |
| 5   | Evitar efectos ocultos (la transacción y el guardado están encapsulados)                         | Caso de uso de ingreso/salida                        | `apps/inventario/application/services.py:40-65` |

## 5. Mapa DDD del módulo

| Elemento DDD                  | Clase(s)                                                             | Archivo                                          |
| ----------------------------- | -------------------------------------------------------------------- | ------------------------------------------------ |
| Entidades                     | `MovimientoInventario`, `AlertaStock`, `MermaDefecto`                | `apps/inventario/domain/stock_prenda.py`         |
| Objeto de Valor               | `Stock` (inmutable, no-negativo)                                     | `apps/inventario/domain/stock_prenda.py`         |
| Agregado                      | `StockPrenda` (raíz; invariantes de ingreso/salida/ajuste y alertas) | `apps/inventario/domain/stock_prenda.py`         |
| Fábrica                       | `InventarioFabrica`                                                  | `apps/inventario/domain/stock_prenda.py`         |
| Repositorios (contratos)      | `RepositorioStock`, `RepositorioMovimiento`, `RepositorioAlerta`     | `apps/inventario/domain/repositorios.py`         |
| Repositorios (implementación) | `DjangoRepositorioStock` y equivalentes                              | `apps/inventario/infrastructure/repositories.py` |
| Servicio                      | `ServicioInventario`                                                 | `apps/inventario/application/services.py`        |
| Módulo                        | App `inventario` con 4 capas                                         | `apps/inventario/`                               |

## 6. Definición de hecho

- [ ] Estilo de programación declarado y evidenciado (sección 2).
- [ ] Los 4 refactors SOLID implementados y evidenciados (sección 3).
- [ ] 5+ prácticas Clean Code evidenciadas (sección 4).
- [ ] Consulta de stock, ingresos, salidas y alertas funcionan (`uv run python manage.py check` + prueba manual de `api/stock/`).
- [ ] Commits solo dentro de `apps/inventario`.
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).
