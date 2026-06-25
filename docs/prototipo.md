# Prototipo Del Sistema

El prototipo muestra el flujo principal de SoftwareTextil desde el inicio de sesión hasta la gestión de catálogo, carrito, inventario, pedidos, despachos, facturación y reportes.

---

## Flujo Principal

```mermaid
flowchart TD
    Login["Iniciar sesion"] --> Panel["Panel principal"]
    Panel --> Catalogo["Catalogo de prendas"]
    Catalogo --> Carrito["Carrito de compras"]
    Carrito --> Pedido["Generar pedido"]
    Pedido --> Pago["Procesar pago"]
    Pedido --> Despacho["Preparar despacho"]
    Despacho --> Guia["Emitir guia de remision"]
    Pago --> Comprobante["Generar comprobante electronico"]
    Comprobante --> Sunat["Consultar estado SUNAT"]
    Panel --> Inventario["Gestionar inventario"]
    Inventario --> Ingreso["Registrar ingreso"]
    Inventario --> Salida["Registrar salida"]
    Panel --> Reportes["Consultar reportes"]
```

---

## Pantallas Del Prototipo

### Login

Pantalla de inicio de sesión para validar el acceso de usuarios registrados.

![Login](../assets/figuras_prototipo/01-login.png)

### Catálogo de Productos

Lista de prendas con filtros y datos comerciales. Permite revisar productos antes de agregarlos al carrito.

![Catálogo de productos](../assets/figuras_prototipo/02-catalogo-productos.png)

### Carrito de Compras

Vista para revisar productos seleccionados, cantidades y totales antes de confirmar el pedido.

![Carrito de compras](../assets/figuras_prototipo/03-carrito-compras.png)

### Registrar Salida de Inventario

Formulario para descontar prendas del almacén por venta, despacho, merma o ajuste.

![Registrar salida](../assets/figuras_prototipo/04-registrar-salida.png)

### Registrar Ingreso de Inventario

Formulario para registrar entradas por producción, compra o devolución.

![Registrar ingreso](../assets/figuras_prototipo/05-registrar-ingreso.png)

### Guía de Remisión

Pantalla para generar el documento que acompaña el traslado físico de prendas.

![Guía de remisión](../assets/figuras_prototipo/06-guia-remision.png)

### Gestión de Pedidos

Vista administrativa para revisar y gestionar pedidos pendientes.

![Gestión de pedidos](../assets/figuras_prototipo/07-gestion-pedidos-admin.png)

### Panel de Control

Dashboard con indicadores de stock, pedidos, movimientos y estado operativo del sistema.

![Panel de control](../assets/figuras_prototipo/08-panel-control-admin.png)

### Generar Comprobante Electrónico

Formulario para generar boletas o facturas electrónicas asociadas a ventas o pedidos.

![Generar comprobante electrónico](../assets/figuras_prototipo/09-generar-comprobante-electronico.png)

### Enviar a Cliente

Pantalla para enviar documentos o notificaciones al cliente.

![Enviar a cliente](../assets/figuras_prototipo/10-enviar-cliente.png)

### Estado SUNAT

Vista para consultar el estado de los comprobantes electrónicos enviados a SUNAT.

![Estado SUNAT](../assets/figuras_prototipo/11-estado-sunat.png)

### Reporte de Emitidos

Listado de comprobantes emitidos y su estado.

![Reporte de emitidos](../assets/figuras_prototipo/12-reporte-emitidos.png)

### Flujo Mobile

Vista del flujo de navegación en dispositivos móviles.

![Flujo mobile](../assets/figuras_prototipo/13-flujo-mobile-zuren.png)

---

## Pantallas Consideradas

| Pantalla | Uso |
| --- | --- |
| Inicio de sesión | Valida usuarios registrados |
| Panel principal | Resume acciones y accesos principales |
| Catálogo | Lista y filtra prendas disponibles |
| Carrito | Permite revisar productos antes del pedido |
| Gestión de pedidos | Administra pedidos pendientes |
| Registro de ingreso | Registra entradas de stock |
| Registro de salida | Registra egresos de stock |
| Guía de remisión | Emite documento para traslado físico |
| Comprobante electrónico | Genera boletas o facturas |
| Estado SUNAT | Consulta aceptación o rechazo del comprobante |
| Reportes | Muestra comprobantes o movimientos emitidos |
| Flujo mobile | Representa navegación adaptada a móviles |

---

## Criterios De Usabilidad

| Criterio | Aplicación |
| --- | --- |
| Claridad | Usa términos del negocio textil |
| Rapidez | Prioriza acciones frecuentes desde el panel principal |
| Trazabilidad | Cada operación conserva fecha, usuario y motivo |
| Control | Las alertas y estados permiten seguimiento operativo |
| Adaptabilidad | El flujo considera escritorio y móvil |
