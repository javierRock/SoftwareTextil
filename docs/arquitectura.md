# Arquitectura

SoftwareTextil usa una arquitectura en capas con enfoque DDD. La aplicacion se organiza como monolito modular para mantener bajo el costo de desarrollo y, a la vez, dejar limites claros entre partes del sistema.

## Capas

| Capa | Responsabilidad |
| --- | --- |
| Presentacion | Recibe peticiones HTTP mediante controladores Flask. |
| Aplicacion | Coordina casos de uso y servicios de aplicacion. |
| Dominio | Contiene entidades, objetos de valor, agregados, servicios de dominio e interfaces de repositorio. |
| Infraestructura | Implementa persistencia con SQLAlchemy y servicios externos. |

## Reglas De Dependencia

| Regla | Aplicacion |
| --- | --- |
| El dominio no depende de frameworks | Las entidades no importan Flask ni SQLAlchemy. |
| La aplicacion depende del dominio | Los servicios usan entidades y repositorios abstractos. |
| La presentacion depende de la aplicacion | Los controladores llaman casos de uso. |
| La infraestructura implementa contratos del dominio | Los repositorios concretos guardan y consultan datos. |

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

    class ServicioPrenda {
        +crear_prenda()
        +buscar_prenda()
        +actualizar_prenda()
        +desactivar_prenda()
    }

    class RepositorioPrenda {
        <<interface>>
        +guardar(prenda)
        +buscar_por_id(id)
        +buscar_por_codigo(codigo)
        +eliminar(id)
    }

    class RepositorioPrendaSQLAlchemy {
        +guardar(prenda)
        +buscar_por_id(id)
        +buscar_por_codigo(codigo)
        +eliminar(id)
    }

    class Prenda {
        +str id
        +str codigo
        +str nombre
        +activar()
        +desactivar()
    }

    PrendaController --> ServicioPrenda
    ServicioPrenda --> RepositorioPrenda
    ServicioPrenda --> Prenda
    RepositorioPrendaSQLAlchemy ..|> RepositorioPrenda
```

## Estructura De Carpetas

```text
src/software_textil/
├── presentation/
│   └── controllers/
├── application/
│   └── services/
├── domain/
│   ├── catalogo/
│   ├── inventario/
│   ├── despachos/
│   ├── usuarios/
│   ├── reportes/
│   └── compartido/
└── infrastructure/
    ├── persistence/
    └── repositories/
```
