<![CDATA[<div align="center">

# 🧵 SoftwareTextil

**Sistema de Gestión de Inventario Textil con Domain-Driven Design**

[![Python](https://img.shields.io/badge/Python-≥3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-≥3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-≥2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![License](https://img.shields.io/badge/Licencia-Académico-blue?style=for-the-badge)](#)

*Proyecto académico de Ingeniería de Software — Universidad Nacional de San Agustín de Arequipa*

---

</div>

## 📋 Tabla de Contenido

- [Descripción](#-descripción)
- [Equipo de Desarrollo](#-equipo-de-desarrollo)
- [Enfoque DDD](#-enfoque-domain-driven-design)
- [Lenguaje Ubicuo](#-lenguaje-ubicuo)
- [Modelo de Dominio](#-modelo-de-dominio)
- [Bounded Contexts y Módulos](#-bounded-contexts-y-módulos)
- [Arquitectura](#-arquitectura)
- [Funcionalidades](#-funcionalidades)
- [API REST](#-api-rest)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Tecnologías](#-tecnologías)
- [Referencias](#-referencias)

---

## 📖 Descripción

**SoftwareTextil** organiza la gestión de inventario de una empresa textil aplicando principios de **Domain-Driven Design (DDD)**. El sistema modela el negocio con conceptos propios del almacén textil: prendas, stock, ingresos, salidas, ajustes, despachos, guías de remisión, alertas y reportes.

El proyecto toma como referencia el estilo de [DDDSample Core](https://github.com/citerus/dddsample-core): separa el dominio de la tecnología, define agregados claros, trabaja con repositorios por agregado y documenta las relaciones del modelo antes de implementar la lógica completa.

> **Objetivo principal:** Ayudar al encargado de inventario a controlar el movimiento diario de prendas en almacén, registrando productos textiles, controlando cantidades disponibles, guardando ingresos y salidas, preparando despachos, generando alertas de stock bajo y entregando reportes para la toma de decisiones.

---

## 👥 Equipo de Desarrollo

| # | Integrante | Rol |
|---|---|---|
| 1 | **Condori Pallardel, Emilio** | Desarrollador |
| 2 | **Gutierrez Castilla, Carlos Enrique** | Desarrollador |
| 3 | **Huayhua Perez, Lizzy Arlette** | Desarrolladora |
| 4 | **Peñalva Humire, Javier Alonzo** | Desarrollador |
| 5 | **Quispe Suarez, Angelo Josué** | Desarrollador |

> **Asignatura:** Ingeniería de Software · **Docente:** Edgar Sarmiento Calisaya  
> **Universidad:** UNSA · **Escuela:** Ciencia de la Computación · **Grupo:** 3ro - A

---

## 🎯 Enfoque Domain-Driven Design

El equipo mantiene las reglas del negocio dentro del dominio. Flask atiende las rutas web, SQLAlchemy resuelve la persistencia y la capa de aplicación coordina los casos de uso. Esta separación permite cambiar detalles técnicos sin tocar las reglas centrales del inventario.

| Concepto DDD | Aplicación en SoftwareTextil |
|---|---|
| **Lenguaje ubicuo** | El equipo usa los mismos términos del negocio: prenda, stock, ingreso, salida, ajuste y despacho. |
| **Agregado** | Cada raíz protege un conjunto de reglas: `Prenda`, `StockPrenda`, `MovimientoInventario`, `Despacho` y `Usuario`. |
| **Objeto de valor** | Valores inmutables como `Cantidad`, `Dinero`, `Talla`, `Color`, `CodigoPrenda` y `PeriodoReporte`. |
| **Repositorio** | Cada agregado expone un contrato de persistencia: `RepositorioStockPrenda`, `RepositorioDespacho`, etc. |
| **Servicio de dominio** | Reglas que no pertenecen a una sola entidad, como `PoliticaStock` para evaluación de stock bajo. |
| **Evento de dominio** | El sistema publica eventos como `StockIngresado`, `StockDescontado` y `DespachoConfirmado`. |
| **Fábrica** | Construcción de agregados complejos mediante `FabricaDespacho`. |

---

## 📚 Lenguaje Ubicuo

El equipo adoptó un **vocabulario compartido** entre desarrolladores y stakeholders del negocio textil:

| Término | Definición en el dominio textil |
|---|---|
| **Prenda** | Producto textil terminado (polo, pantalón, uniforme), listo para venta. |
| **Categoría** | Agrupación comercial de prendas: uniformes, ropa casual, ropa deportiva. |
| **Stock** | Cantidad disponible de una prenda en almacén. |
| **Nivel mínimo** | Umbral de stock que dispara una alerta de reposición. |
| **Ingreso** | Entrada de prendas al almacén por producción, compra o devolución. |
| **Salida** | Egreso de prendas del almacén por venta, despacho, merma o ajuste. |
| **Ajuste** | Corrección manual de stock por conteo físico o deterioro. |
| **Movimiento** | Registro inmutable de un ingreso, salida o ajuste; permite trazabilidad completa. |
| **Despacho** | Proceso de preparación y envío de prendas a un cliente. |
| **Guía de remisión** | Documento que acompaña el despacho físico (requerido por SUNAT). |
| **Alerta de stock bajo** | Notificación automática cuando `stockActual < nivelMinimo`. |

---

## 🏗️ Modelo de Dominio

El modelo de dominio es el corazón de SoftwareTextil. Fue diseñado como un **Diagrama de Clases UML** siguiendo las prácticas de DDD, identificando entidades, objetos de valor, agregados, servicios de dominio y sus relaciones.

### Visión General del Modelo

El siguiente diagrama muestra un ejemplo de cómo se organiza un modelo de dominio con paquetes UML, bounded contexts y las relaciones entre módulos:

<div align="center">

![Ejemplo de organización del Modelo de Dominio](assets/lab05/figura-01-ejemplo-modelo-dominio.png)

*Figura 1 — Ejemplo de organización del Modelo de Dominio con paquetes UML*

</div>

### Gestión de Inventario y Logística

El modelo principal organiza el dominio textil alrededor de **inventario**, **movimientos**, **despachos** y **facturación electrónica** como contexto de soporte:

<div align="center">

![Modelo de dominio de inventario y logística](assets/lab05/figura-02-modelo-inventario-logistica.png)

*Figura 2 — Modelo de dominio: inventario, movimientos, despachos y facturación*

</div>

### Diagrama de Clases del Dominio (Mermaid)

El modelo coloca a `StockPrenda` como **agregado central** del inventario. `Prenda` describe el producto textil, `MovimientoInventario` registra cada cambio de cantidad y `Despacho` agrupa las salidas físicas hacia un cliente.

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

### Relaciones de Entidades Persistentes

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

## 📦 Bounded Contexts y Módulos

El dominio se divide en **contextos delimitados** que agrupan modelos con responsabilidades claramente definidas, siguiendo las prácticas de DDD.

### Módulos de Autenticación y Catálogo

Agrupa entidades y servicios relacionados con autenticación, credenciales, sesiones, catálogo, prendas, tipos de producto y categorías:

<div align="center">

![Módulos de autenticación y catálogo](assets/lab05/figura-04-modulos-autenticacion-catalogo.png)

*Figura 3 — Bounded contexts: autenticación y catálogo de productos*

</div>

### Módulos de Usuarios e Inventario

Muestra módulos para gestión de usuarios, roles, permisos, inventario, stock, movimientos y alertas:

<div align="center">

![Módulos de usuarios e inventario](assets/lab05/figura-05-modulos-usuarios-inventario.png)

*Figura 4 — Bounded contexts: usuarios, roles e inventario*

</div>

### Módulos de Configuración y Reportes

Configuración general del sistema, parámetros y reportes de inventario o ventas:

<div align="center">

![Módulos de configuración y reportes](assets/lab05/figura-06-modulos-configuracion-reportes.png)

*Figura 5 — Bounded contexts: configuración del sistema y reportes*

</div>

### Sistema Contable Textil

Contextos delimitados para autenticación, gestión de ingresos y egresos, inventario, facturación SUNAT, impuestos/declaraciones y cierre/auditoría:

<div align="center">

![Sistema contable textil](assets/lab05/figura-07-sistema-contable-textil.png)

*Figura 6 — Mapa de contextos delimitados del sistema contable textil*

</div>

### Dominio E-Commerce Textil

Agregados y relaciones para usuarios, carrito de compras, historial, pedidos, catálogo de productos, pagos y entregas:

<div align="center">

![Dominio e-commerce textil](assets/lab05/figura-08-dominio-ecommerce-textil.png)

*Figura 7 — Modelo de dominio del e-commerce textil*

</div>

### Mapa de Módulos (Mermaid)

```mermaid
flowchart TB
    subgraph Core["🏭 Núcleo del Negocio"]
        Catalogo["📋 Catálogo\nPrendas, categorías, tallas, colores y precios"]
        Inventario["📦 Inventario\nStock, ingresos, salidas, ajustes y alertas"]
        Despachos["🚚 Despachos\nPreparación, guía de remisión y confirmación"]
    end

    subgraph Soporte["🔧 Contextos de Soporte"]
        Usuarios["👤 Usuarios\nUsuarios, roles y permisos"]
        Reportes["📊 Reportes\nConsultas de stock y movimientos"]
        Compartido["🔗 Compartido\nObjetos de valor y eventos comunes"]
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
|---|---|---|
| **Catálogo** | Mantiene la información comercial de las prendas | `Prenda` |
| **Inventario** | Controla existencias, movimientos y alertas | `StockPrenda`, `MovimientoInventario` |
| **Despachos** | Gestiona la salida física de prendas y su guía de remisión | `Despacho` |
| **Usuarios** | Controla acceso, roles y responsables de movimientos | `Usuario` |
| **Reportes** | Consulta información del inventario sin modificar reglas de negocio | `ReporteInventario` |
| **Compartido** | Comparte objetos de valor, eventos y errores del dominio | `Cantidad`, `Dinero`, `CodigoPrenda` |

---

## 🏛️ Arquitectura

SoftwareTextil usa un **monolito modular** con arquitectura en capas. El proyecto mantiene una sola aplicación desplegable pero separa responsabilidades por capas y módulos de negocio.

### Vista General

```mermaid
flowchart TD
    UsuarioWeb["🌐 Usuario web"] --> Flask["Flask routes / controllers"]
    Flask --> AppServices["Servicios de aplicación\nCasos de uso"]
    AppServices --> DomainModel["Modelo de dominio\nAgregados, objetos de valor y servicios"]
    AppServices --> Ports["Repositorios abstractos\nContratos del dominio"]
    SQLA["Repositorios SQLAlchemy"] --> Ports
    SQLA --> DB[("🗄️ Base de datos relacional")]
    AppServices --> Events["Eventos de dominio"]
    Events --> Reports["Proyección para reportes"]

    classDef outer fill:#e8f1ff,stroke:#2b5fab,stroke-width:2px
    classDef core fill:#fff6d6,stroke:#9a6a00,stroke-width:2px
    classDef infra fill:#e9f8ec,stroke:#2f7d3c,stroke-width:2px

    class UsuarioWeb,Flask outer
    class AppServices,DomainModel,Ports,Events core
    class SQLA,DB,Reports infra
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

### Código Generado desde el Modelo (StarUML → Python)

El modelo de dominio fue diseñado en StarUML y se generó código fuente para Python:

<div align="center">

![Código generado para Python](assets/lab05/figura-03-codigo-generado-python.png)

*Figura 8 — Evidencia de generación de código Python desde StarUML*

</div>

---

## ⚙️ Funcionalidades

### Funcionalidades de Alto Nivel

| Funcionalidad | Descripción |
|---|---|
| 📋 **Gestionar prendas** | Registrar, actualizar, consultar y desactivar prendas del catálogo. |
| 🏷️ **Organizar categorías** | Agrupar prendas por línea comercial, uso, talla o color. |
| 📦 **Controlar stock** | Consultar cantidades disponibles y niveles mínimos. |
| ➕ **Registrar ingresos** | Registrar entradas por producción, compra o devolución. |
| ➖ **Registrar salidas** | Descontar prendas por venta, despacho, merma o ajuste. |
| 🔧 **Ajustar stock** | Corregir diferencias detectadas en conteo físico. |
| 🔔 **Generar alertas** | Detectar prendas con stock por debajo del nivel mínimo. |
| 🚚 **Preparar despachos** | Armar el despacho y asociar movimientos de salida. |
| 📄 **Emitir guía de remisión** | Registrar datos necesarios para el traslado físico. |
| 🔍 **Consultar movimientos** | Revisar historial de ingresos, salidas y ajustes. |
| 📊 **Generar reportes** | Consultar stock, movimientos, alertas y despachos. |
| 👤 **Administrar usuarios** | Gestionar usuarios, roles y permisos. |

### Diagrama de Casos de Uso

```mermaid
flowchart LR
    Encargado["🧑‍💼 Encargado de inventario"]
    Administrador["👨‍💼 Administrador"]
    Vendedor["🛒 Vendedor"]
    Cliente["👤 Cliente"]

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

### Flujo: Registrar Salida de Inventario

```mermaid
sequenceDiagram
    actor Encargado as 🧑‍💼 Encargado de inventario
    participant API as InventarioController
    participant Servicio as ServicioInventario
    participant StockRepo as RepositorioStockPrenda
    participant MovRepo as RepositorioMovimientoInventario
    participant Stock as StockPrenda
    participant DB as 🗄️ Base de datos

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

```text
+--------------------------------------------------------------------------------+
| SoftwareTextil                                      Usuario: Encargado           |
| Inventario textil                                   Fecha: 2026-06-15            |
+-------------------------+------------------------------------------------------+
| Menú                    | Panel principal                                      |
|                         |                                                      |
| 🏠 Inicio               | Indicadores del día                                  |
| 📋 Catálogo              | +----------------+----------------+----------------+ |
| 📦 Inventario            | | Stock bajo: 8  | Movimientos:15 | Despachos: 4   | |
| 🔄 Movimientos           | +----------------+----------------+----------------+ |
| 🚚 Despachos             |                                                      |
| 📊 Reportes              | Acciones rápidas                                     |
| 👤 Usuarios              | [Registrar ingreso] [Registrar salida] [Despachar]  |
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

### Flujo Principal de la GUI

```mermaid
flowchart TD
    Login["🔐 Iniciar sesión"] --> Panel["🏠 Ver panel principal"]
    Panel --> Catalogo["📋 Abrir catálogo"]
    Panel --> Inventario["📦 Consultar inventario"]
    Panel --> Movimientos["🔄 Registrar movimiento"]
    Panel --> Despachos["🚚 Preparar despacho"]
    Panel --> Reportes["📊 Generar reporte"]

    Catalogo --> RegistrarPrenda["Registrar o actualizar prenda"]
    Inventario --> RevisarStock["Revisar stock actual"]
    Inventario --> RevisarAlertas["Atender alertas"]
    Movimientos --> Ingreso["Registrar ingreso"]
    Movimientos --> Salida["Registrar salida"]
    Movimientos --> Ajuste["Registrar ajuste"]
    Despachos --> Guia["Emitir guía de remisión"]
```

---

## 🌐 API REST

SoftwareTextil expone una API RESTful para operaciones de inventario y despachos:

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/prendas` | Lista prendas del catálogo |
| `POST` | `/api/prendas` | Registra una prenda nueva |
| `GET` | `/api/inventario/stock/{prenda_id}` | Consulta stock de una prenda |
| `POST` | `/api/inventario/movimientos` | Registra ingreso, salida o ajuste |
| `GET` | `/api/inventario/movimientos` | Lista movimientos con filtros |
| `POST` | `/api/despachos` | Crea un despacho |
| `POST` | `/api/despachos/{id}/confirmacion` | Confirma un despacho |
| `GET` | `/api/reportes/inventario` | Genera reporte de inventario |

<details>
<summary>📝 Ejemplo de registro de movimiento</summary>

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

</details>

---

## 📁 Estructura del Proyecto

### Diagrama de Paquetes

```mermaid
flowchart TB
    subgraph Root["SoftwareTextil"]
        Docs["📄 docs"]
        Tests["🧪 tests"]

        subgraph Src["src/software_textil"]
            subgraph Presentation["🌐 presentation"]
                Controllers["controllers"]
            end

            subgraph Application["⚙️ application"]
                Services["services"]
                DTOs["dtos"]
            end

            subgraph Domain["🏗️ domain"]
                Catalogo["catalogo"]
                Inventario["inventario"]
                Despachos["despachos"]
                Usuarios["usuarios"]
                Reportes["reportes"]
                Compartido["compartido"]
            end

            subgraph Infrastructure["🔌 infrastructure"]
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

### Árbol de Directorios

```text
SoftwareTextil/
├── 📄 README.md
├── 📄 pyproject.toml
├── 📄 requirements.txt
├── 🖼️ assets/
│   └── lab05/              # Diagramas UML del modelo de dominio
├── 📚 docs/
│   ├── prototipo.md        # Diseño del prototipo de interfaz
│   ├── modelo_dominio.md   # Documentación del modelo de dominio
│   └── arquitectura.md     # Decisiones de arquitectura
├── 🐍 src/
│   └── software_textil/
│       ├── presentation/   # Controladores Flask (rutas HTTP)
│       │   └── controllers/
│       ├── application/    # Casos de uso y DTOs
│       │   ├── dtos/
│       │   └── services/
│       ├── domain/         # Modelo de dominio puro (sin dependencias externas)
│       │   ├── catalogo/
│       │   ├── inventario/
│       │   ├── despachos/
│       │   ├── usuarios/
│       │   ├── reportes/
│       │   └── compartido/
│       └── infrastructure/ # Implementaciones técnicas
│           ├── external_services/
│           ├── persistence/
│           └── repositories/
└── 🧪 tests/
```

---

## 🚀 Instalación y Ejecución

### Prerrequisitos

- **Python** ≥ 3.11
- **pip** (gestor de paquetes)
- **Git**

### Instalación

```bash
# Clonar el repositorio
git clone git@github.com:javierRock/SoftwareTextil.git
cd SoftwareTextil

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

> ⚠️ **Nota:** La aplicación Flask ejecutable se implementará en próximas iteraciones. El punto de entrada estará dentro de `src/software_textil` y conservará la separación entre controladores, servicios, dominio e infraestructura.

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|---|---|
| ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) | Lenguaje principal del proyecto |
| ![Flask](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=white) | Framework web para controladores y rutas HTTP |
| ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) | Mapeo objeto-relacional para persistencia |
| ![Mermaid](https://img.shields.io/badge/-Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white) | Diagramas visibles directamente en GitHub |
| ![StarUML](https://img.shields.io/badge/-StarUML-7D4698?style=flat-square) | Modelado UML formal y generación de código |
| ![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white) | Control de versiones y entrega del repositorio |

---

## 📐 Criterios de Diseño

| Criterio | Aplicación en el proyecto |
|---|---|
| **DDD** | El equipo modela reglas con conceptos del negocio textil |
| **Contextos delimitados** | Catálogo, inventario, despachos, usuarios y reportes mantienen responsabilidades separadas |
| **Agregados** | Cada raíz protege invariantes y evita cambios directos sobre entidades internas |
| **Repositorios** | El dominio declara contratos y la infraestructura implementa persistencia |
| **Arquitectura en capas** | Presentación, aplicación, dominio e infraestructura separados |
| **Bajo acoplamiento** | El dominio no depende de Flask, SQLAlchemy ni detalles de base de datos |
| **Escalabilidad** | Se pueden agregar módulos sin romper el núcleo de inventario |

---

## 📚 Referencias

| Referencia | Uso en el proyecto |
|---|---|
| Evans, E. *Domain-Driven Design* | Guía para entidades, objetos de valor, agregados y repositorios |
| [Citerus DDD Sample Core](https://github.com/citerus/dddsample-core) | Referencia para documentar relaciones de entidades, capas y API |
| [Modern DDD Cargo Tracker](https://github.com/eclipse-ee4j/cargotracker) | Referencia para casos de uso, agregados y separación por módulos |

---

<div align="center">

**Universidad Nacional de San Agustín de Arequipa**  
Facultad de Ingeniería de Producción y Servicios  
Escuela Profesional de Ciencia de la Computación  

*Ingeniería de Software — 2026*

</div>
]]>
