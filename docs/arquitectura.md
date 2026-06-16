# Arquitectura

SoftwareTextil usa una arquitectura en capas con DDD. El equipo trabaja con un monolito modular porque reduce la complejidad inicial y conserva limites claros entre modulos de negocio.

## Capas

| Capa | Responsabilidad |
| --- | --- |
| Presentacion | Recibe peticiones HTTP mediante controladores Flask |
| Aplicacion | Coordina casos de uso y comandos del usuario |
| Dominio | Contiene agregados, objetos de valor, servicios de dominio, eventos e interfaces de repositorio |
| Infraestructura | Implementa persistencia con SQLAlchemy y conecta servicios externos |

## Reglas De Dependencia

| Regla | Aplicacion |
| --- | --- |
| El dominio evita frameworks | Las entidades no importan Flask ni SQLAlchemy |
| La aplicacion usa el dominio | Los servicios coordinan agregados y repositorios abstractos |
| La presentacion usa la aplicacion | Los controladores llaman casos de uso |
| La infraestructura implementa contratos | Los repositorios concretos guardan y consultan datos |

---

## Vista General

```mermaid
flowchart TD
    UsuarioWeb["Usuario web"] --> Flask["Flask routes / controllers"]
    Flask --> AppServices["Servicios de aplicacion"]
    AppServices --> DomainModel["Modelo de dominio"]
    AppServices --> Ports["Repositorios abstractos"]
    SQLA["Repositorios SQLAlchemy"] --> Ports
    SQLA --> DB[("Base de datos relacional")]
    AppServices --> Events["Eventos de dominio"]
    Events --> Reports["Reportes"]
```

---

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

---

## Modelo de Dominio UML (StarUML)

El modelo fue diseñado en StarUML. A continuacion se muestra el diagrama principal del dominio textil.

![Modelo de dominio de inventario y logistica](../assets/lab05/figura-02-modelo-inventario-logistica.png)

### Ejemplo de organizacion del Modelo de Dominio

![Ejemplo de organizacion del Modelo de Dominio](../assets/lab05/figura-01-ejemplo-modelo-dominio.png)

---

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

    class RepositorioMovimiento {
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

    class StockPrendaSQLAlchemy {
        +guardar(stock)
        +buscar_por_prenda(prenda_id)
        +actualizar(stock)
    }

    class MovimientoSQLAlchemy {
        +guardar(movimiento)
        +listar_por_stock(stock_id)
    }

    class DespachoSQLAlchemy {
        +guardar(despacho)
        +buscar_por_id(id)
        +actualizar(despacho)
    }

    InventarioController --> ServicioInventario
    DespachoController --> ServicioDespacho
    ServicioInventario --> RepositorioStockPrenda
    ServicioInventario --> RepositorioMovimiento
    ServicioInventario --> StockPrenda
    ServicioInventario --> MovimientoInventario
    ServicioDespacho --> RepositorioDespacho
    ServicioDespacho --> Despacho
    StockPrendaSQLAlchemy ..|> RepositorioStockPrenda
    MovimientoSQLAlchemy ..|> RepositorioMovimiento
    DespachoSQLAlchemy ..|> RepositorioDespacho
```

---

## Codigo Generado desde StarUML

El modelo fue diseñado en StarUML y se genero codigo fuente para Python.

![Codigo generado para Python](../assets/lab05/figura-03-codigo-generado-python.png)

---

## Flujo Registrar Salida

```mermaid
sequenceDiagram
    actor Encargado as Encargado de inventario
    participant API as InventarioController
    participant Servicio as ServicioInventario
    participant StockRepo as RepositorioStockPrenda
    participant MovRepo as RepositorioMovimiento
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
    Servicio-->>API: Confirma operacion
    API-->>Encargado: Muestra salida registrada
```

---

## Estructura De Carpetas

```
src/software_textil/
├── presentation/     # Controladores Flask
│   └── controllers/
├── application/      # Casos de uso y DTOs
│   ├── dtos/
│   └── services/
├── domain/           # Modelo de dominio puro
│   ├── catalogo/
│   ├── inventario/
│   ├── despachos/
│   ├── usuarios/
│   ├── reportes/
│   └── compartido/
└── infrastructure/   # Implementaciones tecnicas
    ├── external_services/
    ├── persistence/
    └── repositories/
```
