# Inventario React

Módulo independiente en React para visualizar el stock agrupado por categoría.

## Instalación

```bash
npm install
```

## Ejecución

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Lint

```bash
npm run lint
```

## Tests

```bash
npm test
```

## Variable de entorno

Configura la URL base del backend con:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

Si no se define, el frontend usa el origen actual del navegador.

## Endpoint consumido

`GET /api/stock/por-categoria/`

Filtro opcional:

`GET /api/stock/por-categoria/?categoria_id=<id>`

## Estructura

- `src/App.jsx`: composición principal del panel.
- `src/hooks/useInventory.js`: estado, carga, filtro y actualización.
- `src/services/inventoryApi.js`: cliente HTTP del inventario.
- `src/components/`: filtros, tarjetas y estados.
- `src/styles/global.css`: tema visual y layout.

## Integración futura

El panel escucha el evento del navegador `inventory:changed`. Cuando otros módulos registren ingresos o salidas, pueden disparar ese evento con `window.dispatchEvent(new CustomEvent('inventory:changed'))` o usar `notifyInventoryChanged()`.

Para integrarlo en el frontend general, conviene mantener este módulo como microfrontend estático y montarlo en una ruta propia antes de unificar navegación.
