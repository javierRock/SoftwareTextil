# SoftwareTextil

SoftwareTextil organiza la gestión de inventario de una empresa textil con un enfoque de Desarrollo Guiado por Dominio. El equipo modela el negocio con conceptos propios del almacén textil: prendas, stock, ingresos, salidas, ajustes, despachos, guías de remisión, alertas y reportes.

El proyecto toma como referencia el estilo de DDDSample Core: separa el dominio de la tecnología, define agregados claros, trabaja con repositorios por agregado y documenta las relaciones principales del modelo antes de implementar la lógica completa.

## Integrantes

| Integrante |
| --- |
| Condori Pallardel, Emilio Condori |
| Gutierrez Castilla, Carlos Enrique |
| Huayhua Perez, Lizzy Arlette |
| Peñalva Humire, Javier Alonzo |
| Quispe Suarez, Angelo Josué |

## Propósito

SoftwareTextil ayuda al encargado de inventario a controlar el movimiento diario de prendas en almacén. El sistema registra productos textiles, controla cantidades disponibles, guarda ingresos y salidas, prepara despachos, genera alertas de stock bajo y entrega reportes para tomar decisiones rápidas.

El equipo mantiene las reglas del negocio dentro del dominio. Flask atiende las rutas web, SQLAlchemy resuelve la persistencia y la capa de aplicación coordina los casos de uso. Esta separación permite cambiar detalles técnicos sin tocar las reglas centrales del inventario.

## Enfoque DDD

| Concepto DDD | Uso en SoftwareTextil |
| --- | --- |
| Lenguaje ubicuo | El equipo usa los mismos términos del negocio: prenda, stock, ingreso, salida, ajuste y despacho. |
| Agregado | Cada raíz protege un conjunto de reglas: `Prenda`, `StockPrenda`, `MovimientoInventario`, `Despacho` y `Usuario`. |
| Objeto de valor | El dominio modela valores como `Cantidad`, `Dinero`, `Talla`, `Color`, `CodigoPrenda` y `PeriodoReporte`. |
| Repositorio | Cada agregado expone un contrato de persistencia, por ejemplo `RepositorioStockPrenda`. |
| Servicio de dominio | El dominio concentra reglas que no pertenecen a una sola entidad, como la evaluación de stock bajo. |
| Evento de dominio | El sistema puede publicar eventos como `StockIngresado`, `StockDescontado` y `DespachoConfirmado`. |

## Lenguaje Ubicuo

| Término | Definición en el sistema |
| --- | --- |
| Prenda | Producto textil terminado, como polo, pantalón, uniforme o casaca. |
| Categoría | Grupo comercial de prendas, como uniformes, ropa casual o ropa deportiva. |
| Stock | Cantidad disponible de una prenda dentro del almacén. |
| Nivel mínimo | Cantidad límite que activa una alerta de reposición. |
| Ingreso | Entrada de prendas por producción, compra o devolución. |
| Salida | Egreso de prendas por venta, despacho, merma o ajuste. |
| Ajuste | Corrección manual por conteo físico, deterioro o regularización. |
| Movimiento | Registro inmutable de un ingreso, salida o ajuste. |
| Despacho | Preparación y entrega física de prendas a un cliente. |
| Guía de remisión | Documento que acompaña el traslado físico de las prendas. |
| Alerta de stock bajo | Aviso que aparece cuando el stock actual baja del nivel mínimo. |

## Funcionalidades De Alto Nivel

| Funcionalidad | Descripción |
| --- | --- |
| Gestionar prendas | El usuario registra, actualiza, consulta y desactiva prendas del catálogo. |
| Organizar categorías | El usuario agrupa prendas por línea comercial, uso, talla o color. |
| Controlar stock | El encargado consulta cantidades disponibles y niveles mínimos. |
| Registrar ingresos | El encargado registra entradas por producción, compra o devolución. |
| Registrar salidas | El encargado descuenta prendas por venta, despacho, merma o ajuste. |
| Ajustar stock | El encargado corrige diferencias detectadas en conteo físico. |
| Generar alertas | El sistema detecta prendas con stock por debajo del nivel mínimo. |
| Preparar despachos | El encargado arma el despacho y asocia movimientos de salida. |
| Emitir guía de remisión | El sistema registra los datos necesarios para el traslado físico. |
| Consultar movimientos | El usuario revisa el historial de ingresos, salidas y ajustes. |
| Generar reportes | El administrador consulta stock, movimientos, alertas y despachos. |
| Administrar usuarios | El administrador gestiona usuarios, roles y permisos. |

## Diagrama De Casos De Uso UML

```mermaid
flowchart LR
    Encargado["Encargado de inventario"]
    Administrador["Administrador"]
    Vendedor["Vendedor"]
    Cliente["Cliente"]

    subgraph Sistema["SoftwareTextil"]
        UC01((Gestionar prendas))
        UC02((Organizar categorías))
        UC03((Consultar catálogo))
        UC04((Consultar stock))
        UC05((Registrar ingreso))
        UC06((Registrar salida))
        UC07((Ajustar stock))
        UC08((Evaluar stock bajo))
        UC09((Preparar despacho))
        UC10((Emitir guía de remisión))
        UC11((Consultar movimientos))
        UC12((Generar reporte))
        UC13((Gestionar usuarios))
    end

    Encargado --> UC01
    Encargado --> UC02
    Encargado --> UC04
    Encargado --> UC05
    Encargado --> UC06
    Encargado --> UC07
    Encargado --> UC08
    Encargado --> UC09
    Encargado --> UC10
    Encargado --> UC11

    Administrador --> UC12
    Administrador --> UC13
    Administrador --> UC11

    Vendedor --> UC03
    Vendedor --> UC04
    Vendedor --> UC09

    Cliente --> UC09
```

## Prototipo O GUI

El prototipo prioriza operaciones frecuentes del almacén. La pantalla principal muestra indicadores, alertas y accesos rápidos.

```text
+--------------------------------------------------------------------------------+
| SoftwareTextil                                      Usuario: Encargado           |
| Inventario textil                                   Fecha: 2026-06-15            |
+-------------------------+------------------------------------------------------+
| Menú                    | Panel principal                                      |
|                         |                                                      |
| Inicio                  | Indicadores del día                                  |
| Catálogo                | +----------------+----------------+----------------+ |
| Inventario              | | Stock bajo: 8  | Movimientos:15 | Despachos: 4   | |
| Movimientos             | +----------------+----------------+----------------+ |
| Despachos               |                                                      |
| Reportes                | Acciones rápidas                                     |
| Usuarios                | [Registrar ingreso] [Registrar salida] [Despachar]  |
|                         |                                                      |
|                         | Últimos movimientos                                  |
|                         | +------------+----------+----------+---------------+ |
|                         | | Prenda     | Tipo     | Cantidad | Responsable   | |
|                         | +------------+----------+----------+---------------+ |
|                         | | Polo azul  | Salida   | 12       | Almacén       | |
|                         | | Uniforme   | Ingreso  | 30       | Producción    | |
|                         | +------------+----------+----------+---------------+ |
+-------------------------+------------------------------------------------------+
```

## Flujo Principal De La GUI

```mermaid
flowchart TD
    Login["Iniciar sesión"] --> Panel["Ver panel principal"]
    Panel --> Catalogo["Abrir catálogo"]
    Panel --> Inventario["Consultar inventario"]
    Panel --> Movimientos["Registrar movimiento"]
    Panel --> Despachos["Preparar despacho"]
    Panel --> Reportes["Generar reporte"]

    Catalogo --> RegistrarPrenda["Registrar o actualizar prenda"]
    Inventario --> RevisarStock["Revisar stock actual"]
    Inventario --> RevisarAlertas["Atender alertas"]
    Movimientos --> Ingreso["Registrar ingreso"]
    Movimientos --> Salida["Registrar salida"]
    Movimientos --> Ajuste["Registrar ajuste"]
    Despachos --> Guia["Emitir guía de remisión"]
```

## Modelo De Dominio

El modelo coloca a `StockPrenda` como agregado central del inventario. `Prenda` describe el producto textil, `MovimientoInventario` registra cada cambio de cantidad y `Despacho` agrupa las salidas físicas hacia un cliente. El diseño sigue la idea de DDDSample: el dominio expresa reglas de negocio y la infraestructura solo implementa detalles técnicos.

## Diagrama De Clases Del Dominio

```mermaid
classDiagram
    direction LR

    class Prenda {
        <<AggregateRoot>>
        +str id
        +CodigoPrenda codigo
        +str nombre
        +str descripcion
        +Talla talla
        +Color color
        +Dinero precio
        +bool activa
        +activar()
        +desactivar()
        +cambiar_precio(precio)
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
        +str stock_id
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
        +agregar_salida(movimiento)
    }

    class GuiaRemision {
        +str numero
        +datetime fecha_emision
        +str punto_partida
        +str punto_llegada
    }

    class Usuario {
        <<AggregateRoot>>
        +str id
        +str nombre
        +str correo
        +bool activo
        +activar()
        +desactivar()
    }

    class Rol {
        +str id
        +str nombre
    }

    class Cantidad {
        <<ValueObject>>
        +int valor
        +str unidad
        +sumar(otra)
        +restar(otra)
    }

    class Dinero {
        <<ValueObject>>
        +Decimal monto
        +str moneda
    }

    class CodigoPrenda {
        <<ValueObject>>
        +str valor
    }

    class Talla {
        <<ValueObject>>
        +str valor
    }

    class Color {
        <<ValueObject>>
        +str nombre
    }

    class TipoMovimiento {
        <<Enumeration>>
        INGRESO
        SALIDA
        AJUSTE
    }

    class EstadoDespacho {
        <<Enumeration>>
        PENDIENTE
        PREPARADO
        CONFIRMADO
        CANCELADO
    }

    class AlertaStockBajo {
        +str id
        +str stock_id
        +datetime fecha
        +bool atendida
        +marcar_como_atendida()
    }

    class PoliticaStock {
        <<DomainService>>
        +validar_salida(stock, cantidad)
        +evaluar_stock_bajo(stock)
    }

    class FabricaDespacho {
        <<Factory>>
        +crear(cliente, movimientos)
    }

    class StockIngresado {
        <<DomainEvent>>
        +str stock_id
        +Cantidad cantidad
        +datetime ocurrido_en
    }

    class StockDescontado {
        <<DomainEvent>>
        +str stock_id
        +Cantidad cantidad
        +datetime ocurrido_en
    }

    Categoria "1" --> "*" Prenda : agrupa
    Prenda --> CodigoPrenda : identifica
    Prenda --> Talla : usa
    Prenda --> Color : usa
    Prenda --> Dinero : precio
    Prenda "1" --> "1" StockPrenda : controla
    StockPrenda --> Cantidad : cantidad actual
    StockPrenda "1" --> "*" MovimientoInventario : registra
    MovimientoInventario --> TipoMovimiento : clasifica
    MovimientoInventario --> Cantidad : mueve
    StockPrenda "1" --> "*" AlertaStockBajo : genera
    Despacho "1" --> "*" MovimientoInventario : agrupa salidas
    Despacho --> EstadoDespacho : estado
    Despacho "1" --> "0..1" GuiaRemision : emite
    Usuario "1" --> "*" MovimientoInventario : registra
    Usuario "*" --> "1" Rol : tiene
    PoliticaStock ..> StockPrenda : valida
    PoliticaStock ..> AlertaStockBajo : crea
    FabricaDespacho ..> Despacho : construye
    StockPrenda ..> StockIngresado : publica
    StockPrenda ..> StockDescontado : publica
```

## Relaciones De Entidades

Este diagrama cumple la misma función que el diagrama de relaciones del proyecto DDDSample: muestra las entidades persistentes y sus vínculos principales.

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

    CATEGORIA {
        string id
        string nombre
        string descripcion
    }

    PRENDA {
        string id
        string categoria_id
        string codigo
        string nombre
        string talla
        string color
        decimal precio
        boolean activa
    }

    STOCK_PRENDA {
        string id
        string prenda_id
        int cantidad_actual
        int nivel_minimo
        string unidad
    }

    MOVIMIENTO_INVENTARIO {
        string id
        string stock_id
        string despacho_id
        string usuario_id
        string tipo
        int cantidad
        datetime fecha
        string motivo
    }

    DESPACHO {
        string id
        datetime fecha
        string estado
        string cliente
    }

    GUIA_REMISION {
        string numero
        string despacho_id
        datetime fecha_emision
    }

    ALERTA_STOCK_BAJO {
        string id
        string stock_id
        datetime fecha
        boolean atendida
    }

    USUARIO {
        string id
        string rol_id
        string nombre
        string correo
        boolean activo
    }

    ROL {
        string id
        string nombre
    }
```

## Módulos Del Dominio

```mermaid
flowchart TB
    subgraph Core["Núcleo del negocio"]
        Catalogo["Catálogo\nPrendas, categorías, tallas, colores y precios"]
        Inventario["Inventario\nStock, ingresos, salidas, ajustes y alertas"]
        Despachos["Despachos\nPreparación, guía de remisión y confirmación"]
    end

    subgraph Soporte["Contextos de soporte"]
        Usuarios["Usuarios\nUsuarios, roles y permisos"]
        Reportes["Reportes\nConsultas de stock y movimientos"]
        Compartido["Compartido\nObjetos de valor y eventos comunes"]
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

| Módulo | Responsabilidad | Agregados principales |
| --- | --- | --- |
| Catálogo | Mantiene la información comercial de las prendas. | `Prenda` |
| Inventario | Controla existencias, movimientos y alertas. | `StockPrenda`, `MovimientoInventario` |
| Despachos | Gestiona la salida física de prendas y su guía de remisión. | `Despacho` |
| Usuarios | Controla acceso, roles y responsables de movimientos. | `Usuario` |
| Reportes | Consulta información del inventario sin modificar reglas de negocio. | `ReporteInventario` |
| Compartido | Comparte objetos de valor, eventos y errores del dominio. | `Cantidad`, `Dinero`, `CodigoPrenda` |

## Vista General De Arquitectura

SoftwareTextil usa un monolito modular. El proyecto mantiene una sola aplicación desplegable, pero separa responsabilidades por capas y módulos de negocio.

```mermaid
flowchart TD
    UsuarioWeb["Usuario web"] --> Flask["Flask routes / controllers"]
    Flask --> AppServices["Servicios de aplicación\nCasos de uso"]
    AppServices --> DomainModel["Modelo de dominio\nAgregados, objetos de valor y servicios"]
    AppServices --> Ports["Repositorios abstractos\nContratos del dominio"]
    SQLA["Repositorios SQLAlchemy"] --> Ports
    SQLA --> DB[("Base de datos relacional")]
    AppServices --> Events["Eventos de dominio"]
    Events --> Reports["Proyección para reportes"]

    classDef outer fill:#e8f1ff,stroke:#2b5fab,stroke-width:1px
    classDef core fill:#fff6d6,stroke:#9a6a00,stroke-width:1px
    classDef infra fill:#e9f8ec,stroke:#2f7d3c,stroke-width:1px

    class UsuarioWeb,Flask outer
    class AppServices,DomainModel,Ports,Events core
    class SQLA,DB,Reports infra
```

## Diagrama De Paquetes

```mermaid
flowchart TB
    subgraph Root["SoftwareTextil"]
        Docs["docs"]
        Tests["tests"]

        subgraph Src["src/software_textil"]
            subgraph Presentation["presentation"]
                Controllers["controllers"]
            end

            subgraph Application["application"]
                Services["services"]
                DTOs["dtos"]
            end

            subgraph Domain["domain"]
                Catalogo["catalogo"]
                Inventario["inventario"]
                Despachos["despachos"]
                Usuarios["usuarios"]
                Reportes["reportes"]
                Compartido["compartido"]
            end

            subgraph Infrastructure["infrastructure"]
                Persistence["persistence"]
                Repositories["repositories"]
                ApiExternal["external_services"]
            end
        end
    end

    Controllers --> Services
    Services --> Domain
    Repositories --> Domain
    Persistence --> Repositories
    ApiExternal --> Services
    Tests --> Domain
    Tests --> Services
```

## Diagrama De Clases Por Capas

```mermaid
classDiagram
    direction LR

    class InventarioController {
        +consultar_stock()
        +registrar_ingreso()
        +registrar_salida()
        +ajustar_stock()
    }

    class DespachoController {
        +crear_despacho()
        +confirmar_despacho()
        +cancelar_despacho()
    }

    class ServicioInventario {
        +consultar_stock(prenda_id)
        +registrar_ingreso(comando)
        +registrar_salida(comando)
        +ajustar_stock(comando)
    }

    class ServicioDespacho {
        +crear_despacho(comando)
        +confirmar_despacho(id)
        +cancelar_despacho(id)
    }

    class RepositorioStockPrenda {
        <<interface>>
        +guardar(stock)
        +buscar_por_prenda(prenda_id)
        +actualizar(stock)
    }

    class RepositorioMovimientoInventario {
        <<interface>>
        +guardar(movimiento)
        +listar_por_stock(stock_id)
    }

    class RepositorioDespacho {
        <<interface>>
        +guardar(despacho)
        +buscar_por_id(id)
        +actualizar(despacho)
    }

    class StockPrenda {
        +registrar_ingreso(cantidad, motivo)
        +registrar_salida(cantidad, motivo)
        +ajustar(cantidad, motivo)
        +esta_bajo_minimo()
    }

    class MovimientoInventario {
        +crear_ingreso(stock_id, cantidad)
        +crear_salida(stock_id, cantidad)
        +crear_ajuste(stock_id, cantidad)
    }

    class Despacho {
        +preparar()
        +confirmar()
        +cancelar()
        +agregar_salida(movimiento)
    }

    class RepositorioStockPrendaSQLAlchemy {
        +guardar(stock)
        +buscar_por_prenda(prenda_id)
        +actualizar(stock)
    }

    class RepositorioMovimientoSQLAlchemy {
        +guardar(movimiento)
        +listar_por_stock(stock_id)
    }

    class RepositorioDespachoSQLAlchemy {
        +guardar(despacho)
        +buscar_por_id(id)
        +actualizar(despacho)
    }

    InventarioController --> ServicioInventario
    DespachoController --> ServicioDespacho
    ServicioInventario --> RepositorioStockPrenda
    ServicioInventario --> RepositorioMovimientoInventario
    ServicioInventario --> StockPrenda
    ServicioInventario --> MovimientoInventario
    ServicioDespacho --> RepositorioDespacho
    ServicioDespacho --> Despacho
    RepositorioStockPrendaSQLAlchemy ..|> RepositorioStockPrenda
    RepositorioMovimientoSQLAlchemy ..|> RepositorioMovimientoInventario
    RepositorioDespachoSQLAlchemy ..|> RepositorioDespacho
```

## Flujo Del Caso De Uso Registrar Salida

```mermaid
sequenceDiagram
    actor Encargado as Encargado de inventario
    participant API as InventarioController
    participant Servicio as ServicioInventario
    participant StockRepo as RepositorioStockPrenda
    participant MovRepo as RepositorioMovimientoInventario
    participant Stock as StockPrenda
    participant DB as Base de datos

    Encargado->>API: Solicita registrar salida
    API->>Servicio: registrar_salida(comando)
    Servicio->>StockRepo: buscar_por_prenda(prenda_id)
    StockRepo->>DB: SELECT stock
    DB-->>StockRepo: datos de stock
    StockRepo-->>Servicio: StockPrenda
    Servicio->>Stock: registrar_salida(cantidad, motivo)
    Stock-->>Servicio: MovimientoInventario + StockDescontado
    Servicio->>StockRepo: actualizar(stock)
    Servicio->>MovRepo: guardar(movimiento)
    StockRepo->>DB: UPDATE stock
    MovRepo->>DB: INSERT movimiento
    Servicio-->>API: resultado del caso de uso
    API-->>Encargado: confirma salida registrada
```

## API Planificada

SoftwareTextil documenta sus endpoints como DDDSample documenta su API de reportes. La primera versión expone operaciones de inventario y despachos.

| Método | Ruta | Uso |
| --- | --- | --- |
| `GET` | `/api/prendas` | Lista prendas del catálogo. |
| `POST` | `/api/prendas` | Registra una prenda. |
| `GET` | `/api/inventario/stock/{prenda_id}` | Consulta stock de una prenda. |
| `POST` | `/api/inventario/movimientos` | Registra ingreso, salida o ajuste. |
| `GET` | `/api/inventario/movimientos` | Lista movimientos con filtros. |
| `POST` | `/api/despachos` | Crea un despacho. |
| `POST` | `/api/despachos/{id}/confirmacion` | Confirma un despacho. |
| `GET` | `/api/reportes/inventario` | Genera reporte de inventario. |

Ejemplo de registro de movimiento:

```json
{
  "prenda_id": "PRE-001",
  "tipo": "SALIDA",
  "cantidad": 12,
  "unidad": "unidades",
  "motivo": "Despacho a cliente",
  "usuario_id": "USR-001"
}
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
│       │   ├── dtos/
│       │   └── services/
│       ├── domain/
│       │   ├── catalogo/
│       │   ├── inventario/
│       │   ├── despachos/
│       │   ├── usuarios/
│       │   ├── reportes/
│       │   └── compartido/
│       └── infrastructure/
│           ├── external_services/
│           ├── persistence/
│           └── repositories/
└── tests/
```

## Cómo Construir

El proyecto define dependencias para Python. Para preparar el entorno local:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cómo Ejecutar

La siguiente práctica puede agregar la aplicación Flask ejecutable. El equipo mantendrá el punto de entrada dentro de `src/software_textil` y conservará la separación entre controladores, servicios, dominio e infraestructura.

## Tecnologías Elegidas

| Tecnología | Uso |
| --- | --- |
| Python | Lenguaje principal del proyecto. |
| Flask | Framework web para controladores y rutas HTTP. |
| SQLAlchemy | Mapeo objeto-relacional para persistencia. |
| Mermaid | Diagramas visibles directamente en GitHub. |
| StarUML | Herramienta para modelado UML formal si el equipo requiere exportar diagramas. |
| GitHub | Control de versiones y entrega del repositorio. |

## Criterios De Diseño

| Criterio | Aplicación en el proyecto |
| --- | --- |
| DDD | El equipo modela reglas con conceptos del negocio textil. |
| Contextos delimitados | Catálogo, inventario, despachos, usuarios y reportes mantienen responsabilidades separadas. |
| Agregados | Cada raíz protege invariantes y evita cambios directos sobre entidades internas. |
| Repositorios | El dominio declara contratos y la infraestructura implementa persistencia. |
| Arquitectura en capas | El proyecto separa presentación, aplicación, dominio e infraestructura. |
| Bajo acoplamiento | El dominio evita dependencias con Flask, SQLAlchemy y detalles de base de datos. |
| Escalabilidad | El equipo puede agregar módulos sin romper el núcleo de inventario. |

## Referencias

| Referencia | Uso |
| --- | --- |
| Evans, E. Domain-Driven Design | Guía para entidades, objetos de valor, agregados y repositorios. |
| Citerus DDD Sample Core | Referencia para documentar relaciones de entidades, capas y API. |
| Modern DDD Cargo Tracker | Referencia para casos de uso, agregados y separación por módulos. |
