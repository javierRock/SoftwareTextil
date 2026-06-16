# SoftwareTextil

SoftwareTextil es una propuesta universitaria para gestionar el inventario de una empresa textil. El proyecto toma como base el modelo trabajado en `lab05.md`, especialmente el rol de encargado de inventario, el lenguaje ubicuo y los diagramas de inventario, catalogo, usuarios, despachos y reportes.

## Integrantes

| Integrante |
| --- |
| Condori Pallardel, Emilio Condori |
| Gutierrez Castilla, Carlos Enrique |
| Huayhua Perez, Lizzy Arlette |
| Peñalva Humire, Javier Alonzo |
| Quispe Suarez, Angelo Josué |

## Proposito

El proposito de SoftwareTextil es apoyar el control diario del almacen de una empresa textil. El sistema permite registrar prendas, controlar stock, registrar ingresos y salidas, preparar despachos, detectar stock bajo y consultar reportes utiles para tomar decisiones.

El proyecto aplica Desarrollo Guiado por Dominio, conocido como DDD, junto con una arquitectura en capas. La regla principal es separar el negocio textil de los detalles tecnicos. Por eso, las reglas sobre prendas, stock, movimientos y despachos viven en la capa de dominio, mientras que Flask, SQLAlchemy y la base de datos quedan fuera del centro del sistema.

## Fuente Base Del Dominio

El modelo parte de los elementos definidos en `lab05.md`:

| Elemento de `lab05.md` | Uso en este proyecto |
| --- | --- |
| Encargado de inventario | Actor principal del sistema. |
| Prenda | Producto textil terminado, como polo, pantalon o uniforme. |
| Stock | Cantidad disponible de una prenda en almacen. |
| Nivel minimo | Umbral que permite detectar stock bajo. |
| Ingreso | Entrada de prendas al almacen por produccion, compra o devolucion. |
| Salida | Egreso de prendas por venta, despacho, merma o ajuste. |
| Movimiento | Registro inmutable de un ingreso, salida o ajuste. |
| Despacho | Preparacion y envio de prendas a un cliente. |
| Guia de remision | Documento que acompania el traslado fisico de prendas. |
| Alerta de stock bajo | Aviso cuando el stock actual esta por debajo del nivel minimo. |
| Categoria | Agrupacion de prendas por tipo comercial o uso. |

## Funcionalidades De Alto Nivel

| Funcionalidad | Descripcion |
| --- | --- |
| Gestionar prendas | Registrar, actualizar, consultar y desactivar prendas del catalogo. |
| Organizar categorias | Agrupar prendas por lineas como uniformes, ropa casual o ropa deportiva. |
| Controlar stock | Consultar la cantidad disponible de cada prenda en almacen. |
| Registrar ingresos | Registrar entradas por produccion propia, compra o devolucion. |
| Registrar salidas | Registrar egresos por venta, despacho, merma o ajuste. |
| Ajustar stock | Corregir diferencias por conteo fisico, deterioro o regularizacion. |
| Generar alertas | Detectar prendas cuyo stock esta por debajo del nivel minimo. |
| Preparar despachos | Registrar la salida fisica de prendas hacia un cliente. |
| Consultar movimientos | Revisar el historial de ingresos, salidas y ajustes. |
| Generar reportes | Consultar stock, movimientos, alertas y despachos. |
| Administrar usuarios | Gestionar usuarios, roles y permisos de acceso. |

## Diagrama De Casos De Uso UML

```mermaid
flowchart LR
    Encargado["Encargado de inventario"]
    Administrador["Administrador"]
    Vendedor["Vendedor"]

    UC01(["Registrar prenda"])
    UC02(["Actualizar prenda"])
    UC03(["Consultar catalogo"])
    UC04(["Consultar stock"])
    UC05(["Registrar ingreso"])
    UC06(["Registrar salida"])
    UC07(["Ajustar stock"])
    UC08(["Generar alerta de stock bajo"])
    UC09(["Preparar despacho"])
    UC10(["Consultar movimientos"])
    UC11(["Generar reporte de inventario"])
    UC12(["Gestionar usuarios"])

    Encargado --> UC01
    Encargado --> UC02
    Encargado --> UC03
    Encargado --> UC04
    Encargado --> UC05
    Encargado --> UC06
    Encargado --> UC07
    Encargado --> UC08
    Encargado --> UC09
    Encargado --> UC10

    Administrador --> UC11
    Administrador --> UC12
    Administrador --> UC03
    Administrador --> UC04

    Vendedor --> UC03
    Vendedor --> UC04
    Vendedor --> UC09
```

## Prototipo O GUI

El prototipo esta pensado para uso interno. La pantalla principal muestra alertas, movimientos recientes y accesos rapidos a las funciones de inventario.

```text
+--------------------------------------------------------------------------------+
| SoftwareTextil                                                                  |
| Gestion de inventario textil                                                    |
+-------------------------+------------------------------------------------------+
| Menu                    | Panel principal                                      |
|                         |                                                      |
| Inicio                  | Stock bajo: 8 prendas                               |
| Catalogo                | Movimientos del dia: 15                             |
| Inventario              | Despachos pendientes: 4                             |
| Movimientos             |                                                      |
| Despachos               | Ultimos movimientos                                 |
| Reportes                | +------------+----------+----------+---------------+ |
| Usuarios                | | Prenda     | Tipo     | Cantidad | Fecha         | |
|                         | +------------+----------+----------+---------------+ |
|                         | | Polo azul  | Salida   | 12       | 2026-06-15    | |
|                         | | Uniforme   | Ingreso  | 30       | 2026-06-15    | |
|                         | +------------+----------+----------+---------------+ |
+-------------------------+------------------------------------------------------+
```

Pantallas principales:

| Pantalla | Uso |
| --- | --- |
| Inicio de sesion | Permite el ingreso de usuarios registrados. |
| Panel principal | Resume stock bajo, movimientos y despachos pendientes. |
| Catalogo de prendas | Lista prendas con filtros por categoria, talla y color. |
| Registro de prenda | Permite crear o actualizar datos de una prenda. |
| Inventario | Muestra stock actual, nivel minimo y estado de alerta. |
| Movimiento de stock | Registra ingresos, salidas y ajustes. |
| Despachos | Prepara y confirma la salida fisica de prendas. |
| Reportes | Consulta stock, movimientos, alertas y despachos. |

## Modelo De Dominio

El dominio se organiza alrededor del inventario textil. La prenda pertenece al catalogo, el stock representa su disponibilidad en almacen y los movimientos dejan trazabilidad de todo ingreso, salida o ajuste. El despacho usa movimientos de salida y puede generar una guia de remision.

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

    class Talla {
        <<ValueObject>>
        +str valor
    }

    class Color {
        <<ValueObject>>
        +str nombre
    }

    class Dinero {
        <<ValueObject>>
        +float monto
        +str moneda
    }

    class Cantidad {
        <<ValueObject>>
        +int valor
        +str unidad
    }

    class StockPrenda {
        +str id
        +Cantidad cantidad_actual
        +Cantidad nivel_minimo
        +aumentar(cantidad)
        +disminuir(cantidad)
        +ajustar(cantidad)
        +esta_bajo_minimo()
    }

    class MovimientoInventario {
        +str id
        +TipoMovimiento tipo
        +Cantidad cantidad
        +date fecha
        +str motivo
    }

    class TipoMovimiento {
        <<Enumeration>>
        INGRESO
        SALIDA
        AJUSTE
    }

    class AlertaStockBajo {
        +str id
        +date fecha
        +bool atendida
        +marcar_como_atendida()
    }

    class Despacho {
        +str id
        +date fecha
        +EstadoDespacho estado
        +preparar()
        +confirmar()
        +cancelar()
    }

    class EstadoDespacho {
        <<Enumeration>>
        PENDIENTE
        PREPARADO
        CONFIRMADO
        CANCELADO
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

    class ReporteInventario {
        +str id
        +date fecha_generacion
        +generar_resumen()
    }

    class ServicioAlertaStock {
        +evaluar(stock_prenda)
    }

    Categoria "1" --> "*" Prenda : agrupa
    Prenda --> Talla : usa
    Prenda --> Color : usa
    Prenda --> Dinero : precio
    Prenda "1" --> "1" StockPrenda : tiene
    StockPrenda --> Cantidad : controla
    StockPrenda "1" --> "*" MovimientoInventario : registra
    MovimientoInventario --> TipoMovimiento : clasifica
    StockPrenda "1" --> "*" AlertaStockBajo : genera
    Despacho "1" --> "*" MovimientoInventario : confirma salida
    Despacho --> EstadoDespacho : estado
    Despacho "1" --> "0..1" GuiaRemision : documenta
    Usuario "1" --> "*" MovimientoInventario : registra
    Usuario "*" --> "1" Rol : tiene
    ReporteInventario ..> StockPrenda : consulta
    ReporteInventario ..> MovimientoInventario : consulta
    ServicioAlertaStock ..> StockPrenda : evalua
    ServicioAlertaStock ..> AlertaStockBajo : crea
```

## Modulos Del Dominio

Los modulos se definieron a partir de los diagramas del laboratorio 5: gestion de inventario y logistica, autenticacion y catalogo, usuarios e inventario, configuracion y reportes.

```mermaid
flowchart TB
    Sistema["SoftwareTextil"]

    Catalogo["Catalogo\nPrendas, categorias, tallas, colores y precios"]
    Inventario["Inventario\nStock, ingresos, salidas, ajustes y alertas"]
    Despachos["Despachos\nPreparacion, confirmacion y guia de remision"]
    Usuarios["Usuarios\nUsuarios, roles y permisos"]
    Reportes["Reportes\nConsultas de stock, movimientos y alertas"]
    Compartido["Compartido\nValores comunes y reglas reutilizables"]

    Sistema --> Catalogo
    Sistema --> Inventario
    Sistema --> Despachos
    Sistema --> Usuarios
    Sistema --> Reportes
    Sistema --> Compartido

    Catalogo --> Inventario
    Inventario --> Despachos
    Inventario --> Reportes
    Usuarios --> Inventario
    Usuarios --> Despachos
```

| Modulo | Responsabilidad | Agregados principales |
| --- | --- | --- |
| Catalogo | Mantiene la informacion comercial de las prendas. | `Prenda` |
| Inventario | Controla existencias, movimientos y alertas. | `StockPrenda`, `MovimientoInventario` |
| Despachos | Gestiona la salida fisica de prendas. | `Despacho` |
| Usuarios | Controla acceso y permisos. | `Usuario` |
| Reportes | Presenta informacion de consulta para el equipo. | `ReporteInventario` |
| Compartido | Centraliza objetos de valor comunes. | `Cantidad`, `Dinero`, `Talla`, `Color` |

## Vista General De Arquitectura

SoftwareTextil se plantea como un monolito modular. Esto permite trabajar con una sola aplicacion, pero con limites internos claros. La capa de dominio no depende de Flask, SQLAlchemy ni de la base de datos.

```mermaid
flowchart TD
    Presentacion["Presentacion\nControladores Flask y rutas HTTP"]
    Aplicacion["Aplicacion\nServicios de aplicacion y casos de uso"]
    Dominio["Dominio\nEntidades, objetos de valor, agregados y repositorios abstractos"]
    Infraestructura["Infraestructura\nSQLAlchemy, repositorios concretos y servicios externos"]
    BaseDatos[("Base de datos")]

    Presentacion --> Aplicacion
    Aplicacion --> Dominio
    Infraestructura --> Dominio
    Infraestructura --> BaseDatos
```

## Diagrama De Paquetes

```mermaid
flowchart TB
    Proyecto["SoftwareTextil"]

    subgraph SRC["src/software_textil"]
        Presentation["presentation"]
        Application["application"]
        Domain["domain"]
        Infrastructure["infrastructure"]
    end

    Presentation --> Controllers["controllers"]
    Application --> Services["services"]

    Domain --> Catalogo["catalogo"]
    Domain --> Inventario["inventario"]
    Domain --> Despachos["despachos"]
    Domain --> Usuarios["usuarios"]
    Domain --> Reportes["reportes"]
    Domain --> Compartido["compartido"]

    Infrastructure --> Persistence["persistence"]
    Infrastructure --> Repositories["repositories"]

    Proyecto --> SRC
```

## Diagrama De Clases Por Capas

```mermaid
classDiagram
    direction LR

    class PrendaController {
        +crear_prenda()
        +consultar_prenda()
        +actualizar_prenda()
        +desactivar_prenda()
    }

    class StockController {
        +consultar_stock()
        +registrar_ingreso()
        +registrar_salida()
        +ajustar_stock()
    }

    class ServicioPrenda {
        +crear_prenda()
        +buscar_prenda()
        +actualizar_prenda()
        +desactivar_prenda()
    }

    class ServicioInventario {
        +consultar_stock()
        +registrar_ingreso()
        +registrar_salida()
        +ajustar_stock()
        +evaluar_stock_bajo()
    }

    class RepositorioPrenda {
        <<interface>>
        +guardar(prenda)
        +buscar_por_id(id)
        +buscar_por_codigo(codigo)
        +eliminar(id)
    }

    class RepositorioStockPrenda {
        <<interface>>
        +guardar(stock)
        +buscar_por_prenda(prenda_id)
        +actualizar(stock)
    }

    class Prenda {
        +str id
        +str codigo
        +str nombre
        +activar()
        +desactivar()
    }

    class StockPrenda {
        +str id
        +aumentar(cantidad)
        +disminuir(cantidad)
        +esta_bajo_minimo()
    }

    class RepositorioPrendaSQLAlchemy {
        +guardar(prenda)
        +buscar_por_id(id)
        +buscar_por_codigo(codigo)
        +eliminar(id)
    }

    class RepositorioStockPrendaSQLAlchemy {
        +guardar(stock)
        +buscar_por_prenda(prenda_id)
        +actualizar(stock)
    }

    PrendaController --> ServicioPrenda
    StockController --> ServicioInventario
    ServicioPrenda --> RepositorioPrenda
    ServicioPrenda --> Prenda
    ServicioInventario --> RepositorioStockPrenda
    ServicioInventario --> StockPrenda
    RepositorioPrendaSQLAlchemy ..|> RepositorioPrenda
    RepositorioStockPrendaSQLAlchemy ..|> RepositorioStockPrenda
```

## Estructura Del Proyecto

```text
SoftwareTextil/
├── README.md
├── docs/
│   ├── prototipo.md
│   ├── modelo_dominio.md
│   └── arquitectura.md
├── src/
│   └── software_textil/
│       ├── presentation/
│       │   └── controllers/
│       ├── application/
│       │   └── services/
│       ├── domain/
│       │   ├── catalogo/
│       │   ├── inventario/
│       │   ├── despachos/
│       │   ├── usuarios/
│       │   ├── reportes/
│       │   └── compartido/
│       └── infrastructure/
│           ├── persistence/
│           └── repositories/
└── tests/
```

## Tecnologias Elegidas

| Tecnologia | Uso |
| --- | --- |
| Python | Lenguaje principal del proyecto. |
| Flask | Construccion de controladores y rutas web. |
| SQLAlchemy | Mapeo objeto-relacional para persistencia. |
| Mermaid | Diagramas visibles directamente en GitHub. |
| StarUML | Herramienta sugerida para modelado UML formal. |
| GitHub | Control de versiones y entrega del repositorio. |

## Criterios De Disenio

| Criterio | Aplicacion en el proyecto |
| --- | --- |
| DDD | El modelo usa conceptos reales del negocio textil definidos en `lab05.md`. |
| Contextos delimitados | Catalogo, inventario, despachos, usuarios y reportes tienen limites claros. |
| Agregados | Cada grupo importante se protege mediante una raiz como `Prenda`, `StockPrenda` o `Despacho`. |
| Repositorios | El dominio define interfaces y la infraestructura las implementa. |
| Arquitectura en capas | Se separa presentacion, aplicacion, dominio e infraestructura. |
| Bajo acoplamiento | El dominio no conoce Flask, SQLAlchemy ni detalles de base de datos. |
| Escalabilidad | La estructura permite agregar nuevos modulos sin romper el nucleo del sistema. |

## Referencias

| Referencia | Uso |
| --- | --- |
| Evans, E. Domain-Driven Design | Base conceptual para entidades, objetos de valor, agregados y repositorios. |
| Citerus DDD Sample Core | Referencia para separar dominio, aplicacion e infraestructura. |
| Modern DDD Cargo Tracker | Referencia para trabajar con agregados y casos de uso por modulo. |
| `lab05.md` | Fuente original del lenguaje ubicuo y del dominio textil. |
