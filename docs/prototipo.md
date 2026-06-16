# Prototipo Del Sistema

SoftwareTextil presenta una interfaz web para que el encargado de inventario registre operaciones diarias sin perder trazabilidad. A continuación se muestran las pantallas del prototipo organizadas por flujo de usuario.

## Flujo Principal

```mermaid
flowchart TD
    Login["Iniciar sesion"] --> Panel["Ver panel principal"]
    Panel --> Catalogo["Abrir catalogo"]
    Panel --> Inventario["Consultar inventario"]
    Panel --> Movimientos["Registrar movimiento"]
    Panel --> Despachos["Preparar despacho"]
    Panel --> Reportes["Generar reporte"]

    Catalogo --> RegistroPrenda["Registrar o actualizar prenda"]
    Inventario --> StockBajo["Atender stock bajo"]
    Movimientos --> RegistrarIngreso["Registrar ingreso"]
    Movimientos --> RegistrarSalida["Registrar salida"]
    Movimientos --> AjustarStock["Ajustar stock"]
    Despachos --> Guia["Emitir guia de remision"]
    Despachos --> ConfirmarDespacho["Confirmar despacho"]
```

---

## Pantallas Del Prototipo

### Login

Pantalla de inicio de sesion para validar el acceso de usuarios registrados.

![Login](../assets/Prototipo/01-login.png)

### Catalogo de Productos

Lista de prendas con filtros por categoria, talla y color. Permite buscar y seleccionar productos.

![Catalogo de productos](../assets/Prototipo/02-catalogo-productos.png)

### Carrito de Compras

Vista del carrito donde el usuario revisa los productos seleccionados antes de confirmar la operacion.

![Carrito de compras](../assets/Prototipo/03-carrito-compras.png)

### Registrar Salida de Inventario

Formulario para registrar salidas de prendas por venta, despacho, merma o ajuste.

![Registrar salida](../assets/Prototipo/04-registrar-salida.png)

### Registrar Ingreso de Inventario

Formulario para registrar entradas de prendas por produccion, compra o devolucion.

![Registrar ingreso](../assets/Prototipo/05-registrar-ingreso.png)

### Guia de Remision

Pantalla para generar la guia de remision que acompaña el despacho fisico de prendas.

![Guia de remision](../assets/Prototipo/06-guia-remision.png)

### Gestion de Pedidos (Administrador)

Vista del administrador para revisar, aprobar o rechazar pedidos pendientes.

![Gestion de pedidos](../assets/Prototipo/07-gestion-pedidos-admin.png)

### Panel de Control (Administrador)

Dashboard del administrador con indicadores de stock, movimientos y despachos.

![Panel de control](../assets/Prototipo/08-panel-control-admin.png)

### Generar Comprobante Electronico

Pantalla para generar comprobantes electronicos asociados a ventas o despachos.

![Generar comprobante electronico](../assets/Prototipo/09-generar-comprobante-electronico.png)

### Enviar a Cliente

Pantalla para enviar documentos o notificaciones al cliente.

![Enviar a cliente](../assets/Prototipo/10-enviar-cliente.png)

### Estado SUNAT

Vista del estado de los comprobantes ante SUNAT.

![Estado SUNAT](../assets/Prototipo/11-estado-sunat.png)

### Reporte de Emitidos

Reporte con listado de comprobantes emitidos y su estado.

![Reporte de emitidos](../assets/Prototipo/12-reporte-emitidos.png)

### Flujo Mobile

Vista del flujo de la aplicacion en dispositivos moviles.

![Flujo mobile](../assets/Prototipo/13-flujo-mobile-zuren.png)

---

## Pantallas Consideradas

| Pantalla | Uso |
| --- | --- |
| Inicio de sesion | Valida el acceso de usuarios registrados |
| Panel principal | Muestra stock bajo, movimientos y despachos pendientes |
| Catalogo | Lista prendas con filtros por categoria, talla y color |
| Carrito de compras | Revision de productos seleccionados |
| Registro de salida | Registra egresos de prendas del almacen |
| Registro de ingreso | Registra entradas de prendas al almacen |
| Guia de remision | Genera el documento de traslado fisico |
| Gestion de pedidos | Administra pedidos pendientes |
| Panel de control | Dashboard con indicadores del sistema |
| Comprobante electronico | Generacion de comprobantes de venta |
| Estado SUNAT | Consulta de estado ante SUNAT |
| Reportes | Consulta de comprobantes emitidos |
| Flujo mobile | Navegacion en dispositivos moviles |

## Criterios De Usabilidad

| Criterio | Aplicacion |
| --- | --- |
| Claridad | La interfaz usa terminos del almacen textil |
| Rapidez | El panel principal muestra accesos directos a operaciones frecuentes |
| Trazabilidad | Cada movimiento conserva fecha, tipo, cantidad, motivo y usuario |
| Control | Las alertas permiten actuar antes de quedarse sin stock |
