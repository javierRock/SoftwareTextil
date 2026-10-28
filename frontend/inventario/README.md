# Zuren SPA

SPA React 19/Vite para tienda, inventario, catálogo y operaciones de Zuren.

## Instalación

```bash
npm install
```

## Ejecución

```bash
npm run dev
```

Para usar un solo servidor, genera el build y arranca Django desde la raíz del
repositorio:

```bash
npm run build
cd ../..
uv run python manage.py runserver
```

Django sirve la SPA y todas sus rutas en `http://127.0.0.1:8000/`.

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

Si no se define, el frontend usa el origen actual del navegador, que es la
opción recomendada para el build servido por Django.

Vite redirige `/api` y `/media` a `http://localhost:8000` durante desarrollo. La sesión se persiste en `localStorage` bajo `zuren_session` y el cliente central agrega el token Bearer automáticamente.

## Estructura

- `src/services/api.js`: HTTP, errores, autenticación y descargas.
- `src/auth/`: sesión y perfil.
- `src/pages/`: tienda, cliente, inventario y administración.
- `src/components/`: shell, navegación y componentes compartidos.
- `src/styles/global.css`: sistema visual responsive.
