# Arquitectura

SoftwareTextil usa una arquitectura en capas con enfoque DDD. El sistema se organiza como un monolito modular: una sola aplicación desplegable, pero con límites internos claros para catálogo, inventario, e-commerce, despachos, contabilidad y facturación.

---

## Capas

| Capa | Responsabilidad |
| --- | --- |
| Presentación | Recibe peticiones HTTP mediante controladores Flask |
| Aplicación | Coordina casos de uso, DTOs y servicios de aplicación |
| Dominio | Contiene entidades, agregados, objetos de valor, enums y contratos |
| Infraestructura | Implementa persistencia, repositorios y servicios externos |

---

## Reglas De Dependencia

| Regla | Aplicación |
| --- | --- |
| El dominio no depende de frameworks | Las entidades no importan Flask ni SQLAlchemy |
| La aplicación depende del dominio | Los servicios coordinan agregados y repositorios abstractos |
| La presentación depende de aplicación | Los controladores llaman servicios de aplicación |
| La infraestructura implementa contratos | Los repositorios técnicos implementan interfaces del dominio |

---

## Vista General

```mermaid
flowchart TD
    Usuario["Usuario web"] --> Controllers["Controladores Flask"]
    Controllers --> Services["Servicios de aplicacion"]
    Services --> Domain["Modelo de dominio"]
    Services --> Ports["Contratos de repositorio"]
    Repositories["Repositorios SQLAlchemy / memoria"] --> Ports
    Repositories --> DB[("Base de datos")]
    Services --> External["Servicios externos"]
    External --> Sunat["SUNAT"]
```

---

## Módulos Del Monolito

```mermaid
flowchart TB
    subgraph Web["Presentacion"]
        AuthC["auth_controller"]
        CatalogoC["catalogo_controller"]
        InventarioC["inventario_controller"]
        UsuariosC["usuarios_controller"]
        DespachosC["despachos_controller"]
        ContabilidadC["contabilidad_controller"]
        FacturacionC["facturacion_controller"]
    end

    subgraph App["Aplicacion"]
        AuthS["servicio_autenticacion"]
        CatalogoS["servicio_catalogo"]
        InventarioS["servicio_inventario"]
        UsuariosS["servicio_gestion_usuarios"]
        DespachosS["servicio_despachos"]
        ContabilidadS["servicio_contabilidad"]
        FacturacionS["servicio_facturacion"]
    end

    subgraph Domain["Dominio"]
        Catalogo["catalogo"]
        Inventario["inventario"]
        Compras["compras"]
        Pedidos["pedidos"]
        Pagos["pagos"]
        Despachos["despachos"]
        Usuarios["usuarios"]
        Contabilidad["contabilidad"]
        Facturacion["facturacion"]
        Compartido["compartido"]
    end

    Web --> App
    App --> Domain
```

---

## Estructura De Paquetes

```text
src/software_textil/
├── __init__.py              # create_app de Flask
├── bootstrap.py             # Composición de dependencias
├── presentation/
│   └── controllers/         # Blueprints Flask
├── application/
│   ├── dtos/                # DTOs de entrada
│   └── services/            # Casos de uso
├── domain/
│   ├── catalogo/
│   ├── inventario/
│   ├── despachos/
│   ├── usuarios/
│   ├── reportes/
│   ├── contabilidad/
│   ├── facturacion/
│   ├── auditoria/
│   ├── configuracion/
│   └── compartido/
└── infrastructure/
    ├── external_services/   # Integraciones externas, como SUNAT
    ├── persistence/         # Configuración y modelos SQLAlchemy
    └── repositories/        # Implementaciones de repositorios
```

Los módulos `compras`, `pedidos` y `pagos` están definidos por el nuevo modelo UML e-commerce. Su incorporación al código debe seguir la misma separación: dominio puro, servicios de aplicación, controladores e infraestructura.

---

## Controladores Flask

| Blueprint | Responsabilidad |
| --- | --- |
| `auth_controller.py` | Login, logout y validación de sesión |
| `usuarios_controller.py` | Usuarios y roles |
| `catalogo_controller.py` | Prendas, categorías y tipos de producto |
| `inventario_controller.py` | Stock, ingresos, salidas y ajustes |
| `despachos_controller.py` | Creación, preparación, confirmación y cancelación de despachos |
| `contabilidad_controller.py` | Ingresos y egresos contables |
| `facturacion_controller.py` | Emisión de comprobantes electrónicos |
| `reportes_controller.py` | Reportes operativos |
| `configuracion_controller.py` | Parámetros de configuración |

---

## Diagramas UML Relacionados

### Modelo Base

![Modelo de dominio de inventario y logística](../assets/figuras_uml/figura-02-modelo-inventario-logistica.png)

### Encargado de Inventario y Logística

![Encargado de inventario y logística](../assets/figuras_uml/figura-10-encargado-inventario-logistica.png)

### E-commerce: Compras, Pedidos y Pagos

![Módulos de compras pedidos y pagos](../assets/figuras_uml/figura-08-modulos-compras-pedidos-pagos.png)

### Sistema Contable Textil

![Sistema contable textil](../assets/figuras_uml/figura-09-sistema-contable-textil.png)

---

## Flujo Registrar Salida

```mermaid
sequenceDiagram
    actor Encargado as Encargado de inventario
    participant API as InventarioController
    participant Servicio as ServicioInventario
    participant StockRepo as RepositorioInventario
    participant MovRepo as RepositorioMovimientoInventario
    participant Stock as StockPrenda
    participant DB as Base de datos

    Encargado->>API: Solicita registrar salida
    API->>Servicio: registrar_salida(dto)
    Servicio->>StockRepo: buscar_por_prenda(prenda_id)
    StockRepo->>DB: Consulta stock
    DB-->>StockRepo: Datos de stock
    StockRepo-->>Servicio: StockPrenda
    Servicio->>Stock: registrar_salida(cantidad, motivo, usuario_id)
    Stock-->>Servicio: MovimientoInventario
    Servicio->>StockRepo: guardar(stock)
    Servicio->>MovRepo: guardar(movimiento)
    Servicio-->>API: Movimiento registrado
    API-->>Encargado: Confirma salida
```

---

## Criterios Arquitectónicos

| Criterio | Decisión |
| --- | --- |
| Simplicidad inicial | Monolito modular en lugar de microservicios |
| Bajo acoplamiento | Dominio independiente de Flask y SQLAlchemy |
| Trazabilidad | Movimientos, despachos y comprobantes conservan responsables y fechas |
| Evolución | Nuevos módulos se agregan repitiendo el patrón dominio-aplicación-presentación-infraestructura |
| Persistencia | SQLAlchemy queda aislado en infraestructura |
