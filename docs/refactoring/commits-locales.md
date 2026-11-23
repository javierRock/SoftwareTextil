# Trazabilidad de cambios

| Tarjetas | Commit | Verificación |
| --- | --- | --- |
| Q-03, Q-05 | `afc3b6d` | Pruebas de login y dos pruebas de rollback |
| Q-01, S-02, S-03 | `ff73eea` | Suite de ventas y comprobación sin migraciones |
| Q-06 | `6d2eb20` | Pruebas de catálogo y regresión para edición |
| S-01, A-01, A-02 | `7d490ce` | Sonar, revisión estática de CI y prerrequisitos Make |
| Análisis ampliado | `da644a4` | Configuración y exportación SonarQube |
| S-06 | `addd8df` | Pruebas de API React, ESLint y Vite |
| Comparación reproducible | `7785a6a` | Importación equivalente de LCOV en ambas versiones |
| A-03 | `2f1471e` | [Construcción, pruebas y Quality Gate en Jenkins](pipeline-jenkins.md#ejecución-verificada-el-23-de-noviembre-de-2026) |

Desde el repositorio, `git log --oneline origin/dev..refactor/code-quality` y `git show <commit>` permiten revisar los cambios. Consulta las [URLs publicadas de los issues, el Project y los commits](trazabilidad.md).
