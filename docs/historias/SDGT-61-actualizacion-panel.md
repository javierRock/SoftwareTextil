# SDGT-61 — Actualización inmediata del panel

Ruta: `docs/historias/SDGT-61-actualizacion-panel.md`

## 1. Objetivo

Se implementó la actualización inmediata del panel de inventario mediante recarga del endpoint tras cambios exitosos y escucha de un evento desacoplado.

## 2. Componentes involucrados

| Archivo o componente | Responsabilidad |
|---|---|
| `frontend/inventario/src/hooks/useInventory.js` | Reconsulta y conserva el filtro. |
| `frontend/inventario/src/utils/inventoryEvents.js` | Evento `inventory:changed`. |
| `frontend/inventario/src/services/inventoryApi.js` | Fuente única de verdad de datos. |
| `frontend/inventario/src/App.jsx` | Reacciona a `refresh` y estados de carga. |

## 3. Implementación

El hook expone `refresh()` y `setCategoryFilter()`. Cuando otros módulos registren ingreso o salida, pueden disparar `inventory:changed`; el panel escucha ese evento y vuelve a consultar el backend sin perder el filtro activo.

## 4. Estilos de programación usados

| Estilo | Estado | Evidencia | Justificación |
|---|---|---|---|
| Pipeline | Aplicado | Evento → hook → service → render | La actualización sigue un flujo predecible. |
| Error/Exception Handling | Verificado | `ErrorState` solo aparece si la consulta falla | No hay actualización optimista falsa. |
| RESTful | Verificado | La actualización vuelve a `GET /api/stock/por-categoria/` | El estado se sincroniza con la base real. |

Archivo `frontend/inventario/src/hooks/useInventory.js`:

```jsx
  useEffect(() => {
    const handleInventoryChanged = () => {
      refresh();
    };

    window.addEventListener(INVENTORY_CHANGED_EVENT, handleInventoryChanged);
    return () => window.removeEventListener(INVENTORY_CHANGED_EVENT, handleInventoryChanged);
  }, [refresh]);
```

## 5. Prácticas de Clean Code

| Categoría | Práctica | Evidencia |
|---|---|---|
| Nombres | `notifyInventoryChanged`, `INVENTORY_CHANGED_EVENT` | El contrato del evento es explícito. |
| Funciones | `refresh` y `setCategoryFilter` separadas | La UI decide cuándo recargar. |
| Estructura del código fuente | Evento desacoplado en `utils` | No se acopla a los módulos de ingreso/salida. |
| Objetos y estructuras de datos | `CustomEvent` con `detail` opcional | La integración futura queda simple. |
| Tratamiento de errores | Sin actualización optimista | Si falla la consulta, no se muestra un cambio falso. |

## 6. Bugs, code smells y vulnerabilidades

| Tipo | Problema | Corrección | Estado |
|---|---|---|---|
| Regresión visual | Un cambio exitoso podía no reflejarse hasta recargar | Se reconsulta el endpoint tras el evento | Corregido |

## 7. SonarLint y análisis estático

| Herramienta | Rule ID | Hallazgo | Corrección |
|---|---|---|---|
| Revisión manual | No verificado | Sin hallazgos adicionales | N/A |

## 8. Pruebas

| Prueba | Comportamiento | Resultado |
|---|---|---|
| `npm test` | El cliente HTTP sigue funcionando | 2 passed |
| `npm run build` | El panel compila con el listener incluido | Exit 0 |

## 9. Comandos ejecutados

| Comando | Resultado |
|---|---|
| `npm run build` | Exit 0 |
| `npm test` | 2 passed |

## 10. Archivos creados y modificados

- `frontend/inventario/src/hooks/useInventory.js`
- `frontend/inventario/src/utils/inventoryEvents.js`
- `frontend/inventario/src/App.jsx`
- `frontend/inventario/README.md`

## 11. Limitaciones

- La actualización depende de que los módulos de ingreso/salida emitan `inventory:changed` o llamen a `refresh`.

## 12. Conclusión

El panel se sincroniza con la base de datos sin recarga manual y sin optimismo falso.
