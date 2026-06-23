# SoftwareTextil

Sistema de gestión de inventario textil desarrollado con **Domain-Driven Design (DDD)** y arquitectura en capas.

---

## Integrantes

| Integrante | 
| --- |
| Condori Pallardel, Emilio |
| Gutierrez Castilla, Carlos Enrique |
| Huayhua Perez, Lizzy Arlette |
| Peñalva Humire, Javier Alonzo |
| Quispe Suarez, Angelo Josué |

---

## Descripción

SoftwareTextil ayuda al encargado de inventario a controlar el movimiento diario de prendas en almacén. El sistema registra productos textiles, controla cantidades disponibles, guarda ingresos y salidas, prepara despachos, genera alertas de stock bajo y entrega reportes para tomar decisiones rápidas.

El proyecto toma como referencia [DDDSample Core](https://github.com/citerus/dddsample-core): separa el dominio de la tecnología, define agregados claros, trabaja con repositorios por agregado y documenta las relaciones del modelo antes de implementar la lógica completa.

---

## Enfoque DDD

El equipo mantiene las reglas del negocio dentro del dominio. Flask atiende las rutas web, SQLAlchemy resuelve la persistencia y la capa de aplicación coordina los casos de uso.

| Concepto DDD | Aplicación en SoftwareTextil |
| --- | --- |
| Lenguaje ubicuo | Términos del negocio: prenda, stock, ingreso, salida, ajuste, despacho |
| Agregado | Raíces que protegen reglas: `Prenda`, `StockPrenda`, `MovimientoInventario`, `Despacho`, `Usuario` |
| Objeto de valor | Valores inmutables: `Cantidad`, `Dinero`, `Talla`, `Color`, `CodigoPrenda` |
| Repositorio | Contratos de persistencia por agregado: `RepositorioStockPrenda`, `RepositorioDespacho` |
| Servicio de dominio | Reglas transversales: `PoliticaStock` para evaluación de stock bajo |
| Evento de dominio | Eventos publicados: `StockIngresado`, `StockDescontado`, `DespachoConfirmado` |
| Fábrica | Construcción de agregados complejos: `FabricaDespacho` |

---

## Lenguaje Ubicuo

| Término | Definición |
| --- | --- |
| Prenda | Producto textil terminado (polo, pantalón, uniforme), listo para venta |
| Categoría | Agrupación comercial: uniformes, ropa casual, ropa deportiva |
| Stock | Cantidad disponible de una prenda en almacén |
| Nivel mínimo | Umbral que dispara una alerta de reposición |
| Ingreso | Entrada de prendas por producción, compra o devolución |
| Salida | Egreso de prendas por venta, despacho, merma o ajuste |
| Ajuste | Corrección manual por conteo físico o deterioro |
| Movimiento | Registro inmutable de ingreso, salida o ajuste |
| Despacho | Preparación y envío de prendas a un cliente |
| Guía de remisión | Documento que acompaña el despacho físico (requerido por SUNAT) |
| Alerta de stock bajo | Notificación cuando `stockActual < nivelMinimo` |

---

## Modelo de Dominio

El modelo de dominio fue diseñado como un diagrama de clases UML siguiendo las prácticas de DDD: entidades, objetos de valor, agregados, servicios de dominio y sus relaciones.

### Gestión de Inventario y Logística

El modelo principal organiza el dominio textil alrededor de inventario, movimientos, despachos y facturación electrónica.

![Modelo de dominio de inventario y logística](assets/lab05/figura-02-modelo-inventario-logistica.png)

### Diagrama de Clases del Dominio

`StockPrenda` es el agregado central. `Prenda` describe el producto textil, `MovimientoInventario` registra cada cambio de cantidad y `Despacho` agrupa las salidas físicas.

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
    }

    class Rol {
        +str id
        +str nombre
    }

    class Cantidad {
        <<ValueObject>>
        +int valor
        +str unidad
    }

    class Dinero {
        <<ValueObject>>
        +Decimal monto
        +str moneda
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

    Categoria "1" --> "*" Prenda : agrupa
    Prenda "1" --> "1" StockPrenda : controla
    StockPrenda --> Cantidad : cantidad actual
    StockPrenda "1" --> "*" MovimientoInventario : registra
    MovimientoInventario --> TipoMovimiento : clasifica
    StockPrenda "1" --> "*" AlertaStockBajo : genera
    Despacho "1" --> "*" MovimientoInventario : agrupa salidas
    Despacho --> EstadoDespacho : estado
    Despacho "1" --> "0..1" GuiaRemision : emite
    Usuario "1" --> "*" MovimientoInventario : registra
    Usuario "*" --> "1" Rol : tiene
    PoliticaStock ..> StockPrenda : valida
    FabricaDespacho ..> Despacho : construye
```

### Relaciones de Entidades

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

---

## Bounded Contexts y Módulos

El dominio se divide en contextos delimitados con responsabilidades claramente definidas.

### Autenticacion y Catalogo

Entidades y servicios de autenticación, credenciales, sesiones, catálogo, prendas y categorías.

![Modulos de autenticacion y catalogo](assets/lab05/figura-04-modulos-autenticacion-catalogo.png)

### Usuarios e Inventario

Módulos para usuarios, roles, permisos, inventario, stock, movimientos y alertas.

![Modulos de usuarios e inventario](assets/lab05/figura-05-modulos-usuarios-inventario.png)

### Configuracion y Reportes

Configuración general del sistema, parámetros y reportes de inventario o ventas.

![Modulos de configuracion y reportes](assets/lab05/figura-06-modulos-configuracion-reportes.png)

### Sistema Contable Textil

Contextos delimitados para autenticación, gestión de ingresos/egresos, inventario, facturación SUNAT, impuestos y auditoría.

![Sistema contable textil](assets/lab05/figura-07-sistema-contable-textil.png)

### Dominio E-Commerce Textil

Agregados para usuarios, carrito de compras, historial, pedidos, catálogo, pagos y entregas.

![Dominio e-commerce textil](assets/lab05/figura-08-dominio-ecommerce-textil.png)

### Mapa de Modulos

```mermaid
flowchart TB
    subgraph Core["Nucleo del Negocio"]
        Catalogo["Catalogo - Prendas, categorias, tallas, colores y precios"]
        Inventario["Inventario - Stock, ingresos, salidas, ajustes y alertas"]
        Despachos["Despachos - Preparacion, guia de remision y confirmacion"]
    end

    subgraph Soporte["Contextos de Soporte"]
        Usuarios["Usuarios - Usuarios, roles y permisos"]
        Reportes["Reportes - Consultas de stock y movimientos"]
        Compartido["Compartido - Objetos de valor y eventos comunes"]
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

| Modulo | Responsabilidad | Agregados principales |
| --- | --- | --- |
| Catalogo | Informacion comercial de las prendas | `Prenda` |
| Inventario | Existencias, movimientos y alertas | `StockPrenda`, `MovimientoInventario` |
| Despachos | Salida fisica de prendas y guia de remision | `Despacho` |
| Usuarios | Acceso, roles y responsables de movimientos | `Usuario` |
| Reportes | Consulta de informacion sin modificar reglas | `ReporteInventario` |
| Compartido | Objetos de valor, eventos y errores del dominio | `Cantidad`, `Dinero`, `CodigoPrenda` |

---

## Arquitectura

SoftwareTextil usa un monolito modular. Una sola aplicación desplegable con responsabilidades separadas por capas y módulos.

```mermaid
flowchart TD
    UsuarioWeb["Usuario web"] --> Flask["Flask routes / controllers"]
    Flask --> AppServices["Servicios de aplicacion - Casos de uso"]
    AppServices --> DomainModel["Modelo de dominio - Agregados, value objects y servicios"]
    AppServices --> Ports["Repositorios abstractos - Contratos del dominio"]
    SQLA["Repositorios SQLAlchemy"] --> Ports
    SQLA --> DB[("Base de datos relacional")]
    AppServices --> Events["Eventos de dominio"]
    Events --> Reports["Proyeccion para reportes"]
```

### Diagrama de Clases por Capas

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
    ServicioDespacho --> RepositorioDespacho
    ServicioDespacho --> Despacho
    StockPrendaSQLAlchemy ..|> RepositorioStockPrenda
    MovimientoSQLAlchemy ..|> RepositorioMovimiento
    DespachoSQLAlchemy ..|> RepositorioDespacho
```

### Codigo generado desde StarUML

El modelo fue diseñado en StarUML y se generó código fuente para Python.

![Codigo generado para Python](assets/lab05/figura-03-codigo-generado-python.png)

---

## Funcionalidades

| Funcionalidad | Descripcion |
| --- | --- |
| Gestionar prendas | Registrar, actualizar, consultar y desactivar prendas del catalogo |
| Organizar categorias | Agrupar prendas por linea comercial, uso, talla o color |
| Controlar stock | Consultar cantidades disponibles y niveles minimos |
| Registrar ingresos | Registrar entradas por produccion, compra o devolucion |
| Registrar salidas | Descontar prendas por venta, despacho, merma o ajuste |
| Ajustar stock | Corregir diferencias detectadas en conteo fisico |
| Generar alertas | Detectar prendas con stock por debajo del nivel minimo |
| Preparar despachos | Armar el despacho y asociar movimientos de salida |
| Emitir guia de remision | Registrar datos necesarios para el traslado fisico |
| Consultar movimientos | Revisar historial de ingresos, salidas y ajustes |
| Generar reportes | Consultar stock, movimientos, alertas y despachos |
| Administrar usuarios | Gestionar usuarios, roles y permisos |

### Casos de Uso

Los casos de uso fueron organizados por actor principal del sistema.

**Cliente**

![Caso de uso - Cliente](assets/Diagramas_uml/casos-uso/cliente.png)

**Administrador del sistema**

![Caso de uso - Administrador del sistema](assets/Diagramas_uml/casos-uso/administrador-sistema.png)

**Contador**

![Caso de uso - Contador](assets/Diagramas_uml/casos-uso/contador.png)

**Administrador y personal de inventario**

![Caso de uso - Administrador y personal de inventario](assets/Diagramas_uml/casos-uso/administrador-inventario.png)

### Flujo: Registrar Salida

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

### Prototipo de Interfaz

**Login**

![Login](assets/Prototipo/01-login.png)

**Catalogo de productos**

![Catalogo de productos](assets/Prototipo/02-catalogo-productos.png)

**Carrito de compras**

![Carrito de compras](assets/Prototipo/03-carrito-compras.png)

**Registrar salida de inventario**

![Registrar salida](assets/Prototipo/04-registrar-salida.png)

**Registrar ingreso de inventario**

![Registrar ingreso](assets/Prototipo/05-registrar-ingreso.png)

**Guia de remision**

![Guia de remision](assets/Prototipo/06-guia-remision.png)

**Gestion de pedidos (administrador)**

![Gestion de pedidos](assets/Prototipo/07-gestion-pedidos-admin.png)

**Panel de control (administrador)**

![Panel de control](assets/Prototipo/08-panel-control-admin.png)

**Generar comprobante electronico**

![Generar comprobante electronico](assets/Prototipo/09-generar-comprobante-electronico.png)

**Enviar a cliente**

![Enviar a cliente](assets/Prototipo/10-enviar-cliente.png)

**Estado SUNAT**

![Estado SUNAT](assets/Prototipo/11-estado-sunat.png)

**Reporte de emitidos**

![Reporte de emitidos](assets/Prototipo/12-reporte-emitidos.png)

**Flujo mobile**

![Flujo mobile](assets/Prototipo/13-flujo-mobile-zuren.png)

### Flujo de la GUI

```mermaid
flowchart TD
    Login["Iniciar sesion"] --> Panel["Ver panel principal"]
    Panel --> Catalogo["Abrir catalogo"]
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
    Despachos --> Guia["Emitir guia de remision"]
```

---

## API REST

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET` | `/api/prendas` | Lista prendas del catalogo |
| `POST` | `/api/prendas` | Registra una prenda nueva |
| `GET` | `/api/inventario/stock/{prenda_id}` | Consulta stock de una prenda |
| `POST` | `/api/inventario/movimientos` | Registra ingreso, salida o ajuste |
| `GET` | `/api/inventario/movimientos` | Lista movimientos con filtros |
| `POST` | `/api/despachos` | Crea un despacho |
| `POST` | `/api/despachos/{id}/confirmacion` | Confirma un despacho |
| `GET` | `/api/reportes/inventario` | Genera reporte de inventario |

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

---

## Estructura del Proyecto

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

```
SoftwareTextil/
├── README.md
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── assets/
│   ├── Diagramas_uml/        # Diagramas UML por tipo
│   ├── lab05/                # Diagramas UML del modelo de dominio
│   └── Prototipo/            # Capturas del prototipo de interfaz
├── docs/
│   ├── prototipo.md
│   ├── modelo_dominio.md
│   └── arquitectura.md
├── src/
│   └── software_textil/
│       ├── presentation/     # Controladores Flask
│       │   └── controllers/
│       ├── application/      # Casos de uso y DTOs
│       │   ├── dtos/
│       │   └── services/
│       ├── domain/           # Modelo de dominio puro
│       │   ├── catalogo/
│       │   ├── inventario/
│       │   ├── despachos/
│       │   ├── usuarios/
│       │   ├── reportes/
│       │   └── compartido/
│       └── infrastructure/   # Implementaciones tecnicas
│           ├── external_services/
│           ├── persistence/
│           └── repositories/
└── tests/
```

---

## Instalacion

```bash
# Clonar el repositorio
git clone git@github.com:javierRock/SoftwareTextil.git
cd SoftwareTextil

# Crear entorno virtual, resolver e instalar dependencias
uv sync

# Ejecutar la aplicacion Flask
uv run flask --app 'software_textil:create_app()' run --debug
```

`uv` usa `pyproject.toml` como fuente de dependencias y `uv.lock` para instalaciones reproducibles.

---

## Tecnologias

| Tecnologia | Uso |
| --- | --- |
| Python 3.11+ | Lenguaje principal |
| Flask 3.0+ | Framework web para controladores y rutas HTTP |
| SQLAlchemy 2.0+ | Mapeo objeto-relacional para persistencia |
| Mermaid | Diagramas visibles directamente en GitHub |
| StarUML | Modelado UML formal y generacion de codigo |
| GitHub | Control de versiones y entrega del repositorio |

---

## Criterios de Diseno

| Criterio | Aplicacion |
| --- | --- |
| DDD | Reglas modeladas con conceptos del negocio textil |
| Contextos delimitados | Catalogo, inventario, despachos, usuarios y reportes separados |
| Agregados | Cada raiz protege invariantes |
| Repositorios | El dominio declara contratos, la infraestructura implementa |
| Arquitectura en capas | Presentacion, aplicacion, dominio e infraestructura |
| Bajo acoplamiento | El dominio no depende de Flask ni SQLAlchemy |
| Escalabilidad | Modulos nuevos sin romper el nucleo |

---

## Referencias

- Evans, E. *Domain-Driven Design* — Guía para entidades, objetos de valor, agregados y repositorios
- [Citerus DDD Sample Core](https://github.com/citerus/dddsample-core) — Referencia para relaciones de entidades, capas y API
- [Modern DDD Cargo Tracker](https://github.com/eclipse-ee4j/cargotracker) — Referencia para casos de uso y separación por módulos
