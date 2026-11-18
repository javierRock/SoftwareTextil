# Comparación ampliada de calidad

| Verificación | Antes, dev `a312d0a` | Después, rama local `7785a6a` |
| --- | ---: | ---: |
| Issues SonarQube abiertos | 22 | 16 |
| Bugs SonarQube | 1 | 0 |
| Code smells SonarQube | 21 | 16 |
| Vulnerabilidades detectadas por el perfil | 0 | 0 |
| Deuda técnica estimada | 112 min | 82 min |
| Cobertura global SonarQube | 75,3 % | 75,2 % |
| Backend con pytest-cov | 407 aprobadas · 87,65 % | 410 aprobadas · 88,05 % |
| Cliente HTTP con Node | 4 aprobadas | 5 aprobadas |
| Diagnósticos globales Ruff | 58 | 58 |
| Quality Gate | OK en primera línea base, antes de evaluar código nuevo | ERROR · 55,2 % de cobertura nueva frente al 80 % exigido |

SonarQube cerró seis alertas de la línea base. Se corrigieron el fondo CSS de inventario, las referencias repetidas de ventas y tres alertas del cliente HTTP React. La revisión manual aportó cambios en catálogo, pedidos, login, persistencia de roles y automatización.

El análisis comparable usó SonarQube 9.9.7, Scanner 5.0.1 y perfiles Sonar way. Indexó 231 archivos antes y 233 después. Incluyó Python, JavaScript, CSS, HTML y archivos de configuración reconocidos. Make, Jenkins y la configuración de eventos de GitHub Actions se revisaron manualmente. Se excluyeron migraciones, dependencias, builds y ejemplos UML generados. El analizador de Python informó que interpretó 3.11 como 3.10.

SonarQube importó cobertura Python y LCOV del cliente HTTP en ambos análisis. La cobertura global de SonarQube usa un denominador que incluye código fuera de `apps` y frontend con cobertura parcial. Por eso se reporta por separado de pytest-cov. El total de filas del JSON posterior incluye las seis cerradas.

Las rutas personales en los logs publicados se sustituyeron por rutas genéricas. Los resultados de las herramientas se conservaron.

Evidencias [antes](evidencias/ampliada/antes/sonarqube-comparable/metricas.json) · [después](evidencias/ampliada/despues/sonarqube-comparable/metricas.json) · [Quality Gate final](evidencias/ampliada/despues/sonarqube-comparable/quality-gate.json) · [backend](evidencias/ampliada/despues/backend.txt) · [frontend](evidencias/ampliada/despues/frontend.txt) · [make check](evidencias/ampliada/despues/make-check.txt).

ESLint, Vite, los prerrequisitos de Make y las comprobaciones de Django y migraciones pasaron. `make check` se detuvo en Ruff. La validación integral del pipeline Jenkins y del despliegue queda pendiente. El tablero y la trazabilidad se mantienen localmente para revisión.
