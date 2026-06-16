# Modelo De Dominio

SoftwareTextil modela el inventario textil con DDD. El dominio usa términos cercanos al trabajo diario del almacén y protege las reglas mediante agregados, objetos de valor, repositorios y servicios de dominio.

## Lenguaje Ubicuo

| Término | Definición usada en el proyecto |
| --- | --- |
| Prenda | Producto textil terminado, como polo, pantalón, uniforme o casaca. |
| Stock | Cantidad disponible de una prenda en almacén. |
| Nivel mínimo | Cantidad límite que activa una alerta de reposición. |
| Ingreso | Entrada de prendas por producción, compra o devolución. |
| Salida | Egreso de prendas por venta, despacho, merma o ajuste. |
| Ajuste | Corrección manual por conteo físico, deterioro o regularización. |
| Movimiento | Registro inmutable de un ingreso, salida o ajuste. |
| Despacho | Preparación y entrega física de prendas a un cliente. |
| Guía de remisión | Documento que acompaña el traslado físico de las prendas. |
| Alerta de stock bajo | Aviso que aparece cuando el stock actual baja del nivel mínimo. |
| Categoría | Agrupación de prendas por línea comercial o uso. |

## Contextos Delimitados

```mermaid
flowchart TB
    subgraph Core["Núcleo del negocio"]
        Catalogo["Catálogo"]
        Inventario["Inventario"]
        Despachos["Despachos"]
    end

    subgraph Soporte["Contextos de soporte"]
        Usuarios["Usuarios"]
        Reportes["Reportes"]
        Compartido["Compartido"]
    end

    Catalogo --> Inventario
    Inventario --> Despachos
    Inventario --> Reportes
    Usuarios --> Inventario
    Usuarios --> Despachos
    Compartido --> Catalogo
    Compartido --> Inventario
    Compartido --> Despachos
```

| Contexto | Responsabilidad |
| --- | --- |
| Catálogo | Mantiene prendas, categorías, tallas, colores y precios. |
| Inventario | Controla stock, ingresos, salidas, ajustes y alertas. |
| Despachos | Gestiona preparación, confirmación y guía de remisión. |
| Usuarios | Administra usuarios, roles y permisos. |
| Reportes | Consulta stock, movimientos, alertas y despachos. |
| Compartido | Reúne objetos de valor, eventos y errores del dominio. |

## Agregados

| Agregado | Raíz | Repositorio | Invariante principal |
| --- | --- | --- | --- |
| Prenda | `Prenda` | `RepositorioPrenda` | Una prenda mantiene un código único y una categoría válida. |
| Stock | `StockPrenda` | `RepositorioStockPrenda` | El stock no permite salidas mayores a la cantidad disponible. |
| Movimiento | `MovimientoInventario` | `RepositorioMovimientoInventario` | Un movimiento no cambia después de registrarse. |
| Despacho | `Despacho` | `RepositorioDespacho` | Un despacho confirmado no vuelve a estado pendiente. |
| Usuario | `Usuario` | `RepositorioUsuario` | Un usuario activo debe tener un rol asignado. |

## Diagrama De Clases Del Dominio

```mermaid
classDiagram
    direction LR

    class Prenda {
        <<AggregateRoot>>
        +str id
        +CodigoPrenda codigo
        +str nombre
        +Talla talla
        +Color color
        +Dinero precio
        +bool activa
        +activar()
        +desactivar()
    }

    class Categoria {
        +str id
        +str nombre
        +str descripcion
    }

    class StockPrenda {
        <<AggregateRoot>>
        +str id
        +str prenda_id
        +Cantidad cantidad_actual
        +Cantidad nivel_minimo
        +registrar_ingreso(cantidad, motivo)
        +registrar_salida(cantidad, motivo)
        +ajustar(cantidad, motivo)
        +esta_bajo_minimo()
    }

    class MovimientoInventario {
        <<AggregateRoot>>
        +str id
        +TipoMovimiento tipo
        +Cantidad cantidad
        +datetime fecha
        +str motivo
        +str usuario_id
    }

    class Despacho {
        <<AggregateRoot>>
        +str id
        +datetime fecha
        +EstadoDespacho estado
        +preparar()
        +confirmar()
        +cancelar()
    }

    class GuiaRemision {
        +str numero
        +datetime fecha_emision
        +str punto_partida
        +str punto_llegada
    }

    class Cantidad {
        <<ValueObject>>
        +int valor
        +str unidad
    }

    class CodigoPrenda {
        <<ValueObject>>
        +str valor
    }

    class PoliticaStock {
        <<DomainService>>
        +validar_salida(stock, cantidad)
        +evaluar_stock_bajo(stock)
    }

    class StockDescontado {
        <<DomainEvent>>
        +str stock_id
        +Cantidad cantidad
        +datetime ocurrido_en
    }

    Categoria "1" --> "*" Prenda
    Prenda --> CodigoPrenda
    Prenda "1" --> "1" StockPrenda
    StockPrenda --> Cantidad
    StockPrenda "1" --> "*" MovimientoInventario
    MovimientoInventario --> Cantidad
    Despacho "1" --> "*" MovimientoInventario
    Despacho "1" --> "0..1" GuiaRemision
    PoliticaStock ..> StockPrenda
    StockPrenda ..> StockDescontado
```

## Relaciones De Entidades

```mermaid
erDiagram
    CATEGORIA ||--o{ PRENDA : agrupa
    PRENDA ||--|| STOCK_PRENDA : controla
    STOCK_PRENDA ||--o{ MOVIMIENTO_INVENTARIO : registra
    STOCK_PRENDA ||--o{ ALERTA_STOCK_BAJO : genera
    DESPACHO ||--o{ MOVIMIENTO_INVENTARIO : agrupa
    DESPACHO ||--o| GUIA_REMISION : emite
    USUARIO ||--o{ MOVIMIENTO_INVENTARIO : registra
    ROL ||--o{ USUARIO : asigna
```
