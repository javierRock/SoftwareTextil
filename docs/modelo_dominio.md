# Modelo De Dominio

El modelo de dominio se basa en `lab05.md`. El centro del sistema es la gestion de inventario textil, donde la prenda, el stock, los movimientos, los despachos y las alertas forman el nucleo del negocio.

## Lenguaje Ubicuo

| Termino | Definicion usada en el proyecto |
| --- | --- |
| Prenda | Producto textil terminado, como polo, pantalon o uniforme. |
| Stock | Cantidad disponible de una prenda en almacen. |
| Nivel minimo | Cantidad minima esperada para evitar falta de stock. |
| Ingreso | Entrada de prendas al almacen. |
| Salida | Egreso de prendas del almacen. |
| Movimiento | Registro inmutable de ingreso, salida o ajuste. |
| Despacho | Preparacion y envio de prendas a un cliente. |
| Guia de remision | Documento que acompania el traslado fisico. |
| Ajuste | Correccion manual por conteo, deterioro o regularizacion. |
| Alerta de stock bajo | Aviso generado cuando el stock actual es menor al nivel minimo. |
| Categoria | Agrupacion de prendas por tipo o uso. |

## Contextos Delimitados

```mermaid
flowchart TB
    Catalogo["Catalogo"]
    Inventario["Inventario"]
    Despachos["Despachos"]
    Usuarios["Usuarios"]
    Reportes["Reportes"]
    Compartido["Compartido"]

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
| Catalogo | Mantiene prendas, categorias, tallas, colores y precios. |
| Inventario | Controla stock, ingresos, salidas, ajustes y alertas. |
| Despachos | Gestiona preparacion, confirmacion y guia de remision. |
| Usuarios | Administra usuarios, roles y permisos. |
| Reportes | Consulta stock, movimientos, alertas y despachos. |
| Compartido | Reune objetos de valor comunes. |

## Agregados

| Agregado | Raiz | Repositorio |
| --- | --- | --- |
| Prenda | `Prenda` | `RepositorioPrenda` |
| Stock | `StockPrenda` | `RepositorioStockPrenda` |
| Movimiento | `MovimientoInventario` | `RepositorioMovimientoInventario` |
| Despacho | `Despacho` | `RepositorioDespacho` |
| Usuario | `Usuario` | `RepositorioUsuario` |

## Diagrama De Clases Del Dominio

```mermaid
classDiagram
    direction LR

    class Prenda {
        +str id
        +str codigo
        +str nombre
        +str descripcion
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
        +str id
        +int cantidad_actual
        +int nivel_minimo
        +aumentar(cantidad)
        +disminuir(cantidad)
        +ajustar(cantidad)
        +esta_bajo_minimo()
    }

    class MovimientoInventario {
        +str id
        +str tipo
        +int cantidad
        +date fecha
        +str motivo
    }

    class AlertaStockBajo {
        +str id
        +date fecha
        +bool atendida
    }

    class Despacho {
        +str id
        +date fecha
        +str estado
        +preparar()
        +confirmar()
        +cancelar()
    }

    class GuiaRemision {
        +str numero
        +date fecha_emision
    }

    class Usuario {
        +str id
        +str nombre
        +str correo
        +bool activo
    }

    class Rol {
        +str id
        +str nombre
    }

    Categoria "1" --> "*" Prenda
    Prenda "1" --> "1" StockPrenda
    StockPrenda "1" --> "*" MovimientoInventario
    StockPrenda "1" --> "*" AlertaStockBajo
    Despacho "1" --> "*" MovimientoInventario
    Despacho "1" --> "0..1" GuiaRemision
    Usuario "1" --> "*" MovimientoInventario
    Usuario "*" --> "1" Rol
```
