# Comparación de calidad

Esta comparación corresponde al análisis inicial de `apps` y `config`. Para la entrega actual, consulta la [comparación ampliada](resultado-ampliado.md).

| Indicador | Antes | Después |
| --- | --- | --- |
| Commit analizado | a312d0a | Árbol local sobre a312d0a, sin commit |
| Pruebas y cobertura pytest-cov | 407 aprobadas; 87,65 %; umbral 85 % superado | 409 aprobadas; 87,88 %; umbral 85 % superado |
| Ruff | 58 diagnósticos globales | 58 diagnósticos globales; revisión focalizada aprobada |
| SonarQube: bugs | 1 | 0 |
| SonarQube: vulnerabilidades | 0 | 0 |
| SonarQube: code smells | 7 | 5 |
| SonarQube: deuda técnica | 39 minutos estimados por la herramienta | 25 minutos |
| SonarQube: cobertura, alcance apps y config | 86,3 % | 86,5 % |
| Quality Gate | PASSED | PASSED (API: OK) |

Guardar versión del servidor/scanner, perfil de calidad, exclusiones, cobertura importada, fecha y commit de ambos análisis. Comparar con configuración idéntica y verificar que la tarea de análisis terminó antes de exportar resultados.

Capturas previstas: resumen SonarQube antes/después, detalle de issues corregidos, tablero y responsables, diff del código, pruebas verdes y commits vinculados.

La ejecución después corresponde al árbol de trabajo sin commit, no a un SHA nuevo. Los logs `sonar-scanner-final.txt` y los JSON exportados contienen el último resultado. Los logs previos con errores de rutas quedan solo como diagnóstico y no son los resultados comparados.

La exportación de issues conserva también los cerrados. Para contar los pendientes, filtrar por estado distinto de CLOSED; para los totales de calidad usar `metricas.json`. No se cerraron issues manualmente para mejorar las cifras.

Se comprobó que los cambios de constantes no generan migraciones. Django advierte que falta el build del frontend React en este worktree; este paquete valida refactorización y pruebas del backend y no es un artefacto de despliegue frontend.
