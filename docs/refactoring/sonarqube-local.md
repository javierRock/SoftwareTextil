# Comparación en SonarQube local

El 23 de noviembre de 2026 se escanearon dos copias limpias en [SoftwareTextil - Comparacion de refactorizacion](http://localhost:9000/dashboard?id=softwaretextil-refactoring-compare). La línea base usa [`a312d0a` de `dev`](https://github.com/javierRock/SoftwareTextil/commit/a312d0ad8ba7199d28782371a08b62f590c95679). La segunda pasada usa [`7785a6a`](https://github.com/javierRock/SoftwareTextil/commit/7785a6a689518d4e0e1eae9df43218670fb49de4). Se exportó y capturó la línea base antes de enviar la segunda pasada.

La instancia usa **SonarQube Community Build 25.1.0, modo MQR** y **SonarScanner CLI 7.2.0**. Ambas pasadas usaron perfiles Sonar way, las mismas exclusiones y cobertura importada de Python 3.11 y Node 26.13.1. Python entregó 407 → 410 pruebas aprobadas con 87,65 % → 88,05 % de cobertura en pytest-cov. El scanner importó el XML de Python y el LCOV de las pruebas del cliente HTTP en las dos pasadas.

| Medida | `dev`, 11:32:11 | Código refactorizado, 11:34:51 |
| --- | ---: | ---: |
| Issues abiertos únicos | 118 | 113 |
| Hallazgos con impacto en confiabilidad | 82 | 81 |
| Hallazgos con impacto en mantenibilidad | 104 | 100 |
| Hallazgos con impacto en seguridad | 0 | 0 |
| Puntos de revisión de seguridad | 1 | 1 |
| Deuda técnica estimada | 564 min | 540 min |
| Cobertura global SonarQube | 75,3 % | 75,2 % |
| Cobertura de código nuevo | Línea base | 55,2 % |
| Quality Gate | Aprobado en la línea base | Falló por cobertura de código nuevo (mínimo 80 %) |

Horas de Lima. Un issue puede afectar más de una cualidad en el modo MQR. La [comparación histórica](resultado-ampliado.md) usó SonarQube 9.9.7 y registró 22 → 16 issues. Cada comparación usa los recuentos de su propio servidor y perfil.

- **Antes.** [Análisis](evidencias/sonarqube-local-2026-11-23/antes/analisis.json) · [Métricas](evidencias/sonarqube-local-2026-11-23/antes/metricas.json) · [Issues](evidencias/sonarqube-local-2026-11-23/antes/issues.json) · [Gate](evidencias/sonarqube-local-2026-11-23/antes/quality-gate.json) · [Scanner](evidencias/sonarqube-local-2026-11-23/antes/scanner.txt).
- **Después.** [Análisis](evidencias/sonarqube-local-2026-11-23/despues/analisis.json) · [Métricas](evidencias/sonarqube-local-2026-11-23/despues/metricas.json) · [Issues](evidencias/sonarqube-local-2026-11-23/despues/issues.json) · [Gate](evidencias/sonarqube-local-2026-11-23/despues/quality-gate.json) · [Scanner](evidencias/sonarqube-local-2026-11-23/despues/scanner.txt).

## Capturas de la comparación

| Captura | Qué muestra |
| --- | --- |
| [Línea base](evidencias/capturas-exposicion/04-sonarqube-antes.png) | `a312d0a`, 23 de noviembre a las 11:32. SonarQube registra 118 issues únicos, 75,3 % de cobertura global y Gate aprobado. |
| [Después del refactor](evidencias/capturas-exposicion/05-sonarqube-despues.png) | `7785a6a`, a las 11:34. SonarQube registra 113 issues únicos, 75,2 % de cobertura global y Gate fallido. |
| [Cobertura de código nuevo](evidencias/capturas-exposicion/06-quality-gate.png) | El análisis posterior registra 55,2 % de cobertura de código nuevo frente al 80 % exigido. |

El [build #5 de Jenkins](pipeline-jenkins.md#validación-posterior-en-jenkins) documenta la validación posterior en otro commit y con una clave de SonarQube separada.

Consulta la [matriz de tareas](matriz.md), la [trazabilidad del PR](trazabilidad.md) y el [pipeline Jenkins para `dev`](pipeline-jenkins.md).
