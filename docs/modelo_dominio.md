# Modelo De Dominio

SoftwareTextil modela el inventario textil con DDD. El dominio usa terminos cercanos al trabajo diario del almacen y protege las reglas mediante agregados, objetos de valor, repositorios y servicios de dominio.

## Lenguaje Ubicuo

| Termino | Definicion |
| --- | --- |
| Prenda | Producto textil terminado, como polo, pantalon, uniforme o casaca |
| Stock | Cantidad disponible de una prenda en almacen |
| Nivel minimo | Cantidad limite que activa una alerta de reposicion |
| Ingreso | Entrada de prendas por produccion, compra o devolucion |
| Salida | Egreso de prendas por venta, despacho, merma o ajuste |
| Ajuste | Correccion manual por conteo fisico, deterioro o regularizacion |
| Movimiento | Registro inmutable de un ingreso, salida o ajuste |
| Despacho | Preparacion y entrega fisica de prendas a un cliente |
| Guia de remision | Documento que acompaña el traslado fisico de las prendas |
| Alerta de stock bajo | Aviso que aparece cuando el stock actual baja del nivel minimo |
| Categoria | Agrupacion de prendas por linea comercial o uso |

---

## Modelo de Dominio UML (StarUML)

Modelo principal que organiza el dominio textil alrededor de inventario, movimientos, despachos y facturacion electronica.

![Modelo de dominio de inventario y logistica](../assets/lab05/figura-02-modelo-inventario-logistica.png)

---

## Contextos Delimitados

```mermaid
flowchart TB
    subgraph Core["Nucleo del negocio"]
        Catalogo["Catalogo"]
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
| Catalogo | Mantiene prendas, categorias, tallas, colores y precios |
| Inventario | Controla stock, ingresos, salidas, ajustes y alertas |
| Despachos | Gestiona preparacion, confirmacion y guia de remision |
| Usuarios | Administra usuarios, roles y permisos |
| Reportes | Consulta stock, movimientos, alertas y despachos |
| Compartido | Objetos de valor, eventos y errores del dominio |

---

## Modulos del Dominio (StarUML)

### Autenticacion y Catalogo

Entidades y servicios de autenticacion, credenciales, sesiones, catalogo, prendas y categorias.

![Modulos de autenticacion y catalogo](../assets/lab05/figura-04-modulos-autenticacion-catalogo.png)

### Usuarios e Inventario

Modulos para usuarios, roles, permisos, inventario, stock, movimientos y alertas.

![Modulos de usuarios e inventario](../assets/lab05/figura-05-modulos-usuarios-inventario.png)

### Configuracion y Reportes

Configuracion general del sistema, parametros y reportes de inventario o ventas.

![Modulos de configuracion y reportes](../assets/lab05/figura-06-modulos-configuracion-reportes.png)

### Sistema Contable Textil

Contextos delimitados para autenticacion, gestion de ingresos/egresos, inventario, facturacion SUNAT, impuestos y auditoria.

![Sistema contable textil](../assets/lab05/figura-07-sistema-contable-textil.png)

### Dominio E-Commerce Textil

Agregados y relaciones para usuarios, carrito de compras, historial, pedidos, catalogo, pagos y entregas.

![Dominio e-commerce textil](../assets/lab05/figura-08-dominio-ecommerce-textil.png)

---

## Agregados

| Agregado | Raiz | Repositorio | Invariante principal |
| --- | --- | --- | --- |
| Prenda | `Prenda` | `RepositorioPrenda` | Una prenda mantiene un codigo unico y una categoria valida |
| Stock | `StockPrenda` | `RepositorioStockPrenda` | El stock no permite salidas mayores a la cantidad disponible |
| Movimiento | `MovimientoInventario` | `RepositorioMovimientoInventario` | Un movimiento no cambia despues de registrarse |
| Despacho | `Despacho` | `RepositorioDespacho` | Un despacho confirmado no vuelve a estado pendiente |
| Usuario | `Usuario` | `RepositorioUsuario` | Un usuario activo debe tener un rol asignado |

---

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

---

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

---

## Codigo Generado desde StarUML

El modelo fue diseñado en StarUML y se genero codigo fuente para Python.

![Codigo generado para Python](../assets/lab05/figura-03-codigo-generado-python.png)
