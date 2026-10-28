# SDGT-58 — Panel React de inventario

Ruta: `docs/historias/SDGT-58-panel-inventario-react.md`

## 1. Objetivo

Se creó un frontend React independiente para visualizar el stock agrupado por categoría con filtro, estados de carga/error/vacío y diseño responsive.

## 2. Componentes involucrados

| Archivo o componente | Responsabilidad |
|---|---|
| `frontend/inventario/package.json` | Scripts y dependencias del módulo. |
| `frontend/inventario/src/App.jsx` | Composición del panel. |
| `frontend/inventario/src/hooks/useInventory.js` | Estado, carga y filtro. |
| `frontend/inventario/src/services/inventoryApi.js` | Cliente HTTP. |
| `frontend/inventario/src/components/*` | UI por bloques. |
| `frontend/inventario/src/styles/global.css` | Tema visual y responsive. |

## 3. Implementación

El panel consume el endpoint agrupado, conserva el filtro seleccionado y muestra tarjetas por categoría con sus prendas y cantidades. El diseño se basó en la composición y la paleta del HTML de referencia, pero llevado a componentes React.

## 4. Estilos de programación usados

| Estilo | Estado | Evidencia | Justificación |
|---|---|---|---|
| Pipeline | Aplicado | `useInventory -> inventoryApi -> App -> components` | El dato viaja por etapas claras. |
| RESTful | Verificado | Consumidor de `GET /api/stock/por-categoria/` | El frontend no acopla reglas al backend. |
| Error/Exception Handling | Aplicado | `ErrorState` + throw en `inventoryApi.js` | El error se muestra sin falsos positivos. |

Archivo `frontend/inventario/src/App.jsx`:

```jsx
        <main className="content" aria-live="polite">
          {isLoading ? <LoadingState /> : null}
          {!isLoading && error ? <ErrorState message={error} onRetry={refresh} /> : null}
          {!isLoading && !error && data.length === 0 ? <EmptyState /> : null}
          {!isLoading && !error && data.length > 0 ? (
            <div className="category-grid">
              {data.map((category) => (
                <CategoryStockCard key={category.categoria_id} category={category} />
              ))}
            </div>
          ) : null}
        </main>
```

## 5. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
|---|---|---|
| Nombres | `CategoryStockCard`, `useInventory` | Los nombres describen intención. |
| Funciones | `buildInventoryUrl`, `fetchGroupedStockByCategory` | Lógica HTTP aislada del UI. |
| Comentarios | README con integración futura | La integración queda documentada. |
| Estructura del código fuente | Carpetas `components`, `hooks`, `services`, `styles` | Separación por responsabilidad. |
| Objetos y estructuras de datos | Respuesta agrupada tipada por contrato | La UI recibe datos ya normalizados. |
| Tratamiento de errores | `ErrorState` y `parseErrorResponse` | El estado de error es explícito. |
| Clases | No aplicable | El frontend usa funciones y hooks. |

## 6. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
|---|---|---|---|
| Riesgo visual | CSS genérico podía verse plano | Se aplicó un tema con tipografía y profundidad | Corregido |

## 7. SonarLint y análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
|---|---|---|---|
| Revisión manual | No verificado | Sin hallazgos manuales adicionales | N/A |

## 8. Pruebas

| Prueba | Comportamiento | Resultado |
|---|---|---|
| `npm test` | Valida URL y cliente HTTP | 2 passed |
| `npm run build` | Compilación del módulo React | Exit 0 |
| `npm run lint` | Verificación estática | Exit 0 |

## 9. Comandos ejecutados

| Comando | Resultado |
|---|---|
| `npm install` | Dependencias instaladas |
| `npm run lint` | Exit 0 |
| `npm run build` | Exit 0 |
| `npm test` | 2 passed |

## 10. Archivos creados y modificados

- `frontend/inventario/package.json`
- `frontend/inventario/index.html`
- `frontend/inventario/vite.config.js`
- `frontend/inventario/eslint.config.js`
- `frontend/inventario/src/main.jsx`
- `frontend/inventario/src/App.jsx`
- `frontend/inventario/src/components/CategoryFilter.jsx`
- `frontend/inventario/src/components/CategoryStockCard.jsx`
- `frontend/inventario/src/components/StockItem.jsx`
- `frontend/inventario/src/components/LoadingState.jsx`
- `frontend/inventario/src/components/EmptyState.jsx`
- `frontend/inventario/src/components/ErrorState.jsx`
- `frontend/inventario/src/hooks/useInventory.js`
- `frontend/inventario/src/services/inventoryApi.js`
- `frontend/inventario/src/services/inventoryApi.test.js`
- `frontend/inventario/src/utils/inventoryEvents.js`
- `frontend/inventario/src/styles/global.css`
- `frontend/inventario/README.md`

## 11. Limitaciones

- El módulo corre independiente; aún no está integrado al frontend general del sistema.

## 12. Conclusión

El panel React quedó funcional, responsive y alineado al panel de referencia.
