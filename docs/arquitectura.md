# Arquitectura

SoftwareTextil usa una arquitectura en capas con DDD. El equipo trabaja con un monolito modular porque este estilo reduce la complejidad inicial y conserva límites claros entre módulos de negocio.

## Capas

| Capa | Responsabilidad |
| --- | --- |
| Presentación | Recibe peticiones HTTP mediante controladores Flask. |
| Aplicación | Coordina casos de uso y comandos del usuario. |
| Dominio | Contiene agregados, objetos de valor, servicios de dominio, eventos e interfaces de repositorio. |
| Infraestructura | Implementa persistencia con SQLAlchemy y conecta servicios externos. |

## Reglas De Dependencia

| Regla | Aplicación |
| --- | --- |
| El dominio evita frameworks | Las entidades no importan Flask ni SQLAlchemy. |
| La aplicación usa el dominio | Los servicios coordinan agregados y repositorios abstractos. |
| La presentación usa la aplicación | Los controladores llaman casos de uso. |
| La infraestructura implementa contratos | Los repositorios concretos guardan y consultan datos. |

## Vista General

```mermaid
flowchart TD
    UsuarioWeb["Usuario web"] --> Flask["Flask routes / controllers"]
    Flask --> AppServices["Servicios de aplicación"]
    AppServices --> DomainModel["Modelo de dominio"]
    AppServices --> Ports["Repositorios abstractos"]
    SQLA["Repositorios SQLAlchemy"] --> Ports
    SQLA --> DB[("Base de datos relacional")]
    AppServices --> Events["Eventos de dominio"]
    Events --> Reports["Reportes"]
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
                External["external_services"]
            end
        end
    end

    Controllers --> Services
    Services --> Domain
    Repositories --> Domain
    Persistence --> Repositories
    External --> Services
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

    class ServicioInventario {
        +consultar_stock(prenda_id)
        +registrar_ingreso(comando)
        +registrar_salida(comando)
        +ajustar_stock(comando)
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

    class RepositorioStockPrendaSQLAlchemy {
        +guardar(stock)
        +buscar_por_prenda(prenda_id)
        +actualizar(stock)
    }

    class RepositorioMovimientoSQLAlchemy {
        +guardar(movimiento)
        +listar_por_stock(stock_id)
    }

    InventarioController --> ServicioInventario
    ServicioInventario --> RepositorioStockPrenda
    ServicioInventario --> RepositorioMovimientoInventario
    ServicioInventario --> StockPrenda
    ServicioInventario --> MovimientoInventario
    RepositorioStockPrendaSQLAlchemy ..|> RepositorioStockPrenda
    RepositorioMovimientoSQLAlchemy ..|> RepositorioMovimientoInventario
```

## Flujo Registrar Salida

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
    StockRepo->>DB: Consulta stock
    DB-->>StockRepo: Devuelve stock
    StockRepo-->>Servicio: Entrega StockPrenda
    Servicio->>Stock: registrar_salida(cantidad, motivo)
    Stock-->>Servicio: Devuelve movimiento y evento
    Servicio->>StockRepo: actualizar(stock)
    Servicio->>MovRepo: guardar(movimiento)
    StockRepo->>DB: Actualiza stock
    MovRepo->>DB: Inserta movimiento
    Servicio-->>API: Confirma operación
    API-->>Encargado: Muestra salida registrada
```

## Estructura De Carpetas

```text
src/software_textil/
├── presentation/
│   └── controllers/
├── application/
│   ├── dtos/
│   └── services/
├── domain/
│   ├── catalogo/
│   ├── inventario/
│   ├── despachos/
│   ├── usuarios/
│   ├── reportes/
│   └── compartido/
└── infrastructure/
    ├── external_services/
    ├── persistence/
    └── repositories/
```
