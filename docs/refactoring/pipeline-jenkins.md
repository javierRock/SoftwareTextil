# Integración continua de SoftwareTextil en Jenkins

El `Jenkinsfile` del [PR #46](https://github.com/javierRock/SoftwareTextil/pull/46) está preparado para un job Pipeline desde SCM que construya la rama `dev`. La [matriz](matriz.md) contiene los hallazgos por módulo, responsable, prioridad y estrategia. La [trazabilidad](trazabilidad.md) enlaza los issues, el Kanban y los commits.

## Configuración del job

- Usar **Pipeline script from SCM**, el repositorio `javierRock/SoftwareTextil`, la rama `*/dev` y la ruta `Jenkinsfile`. Para validar el PR antes de integrarlo, usar otro job que lea `*/refactor/code-quality`.
- El agente necesita Git, Make, Docker Compose, uv, Python 3.11, Node 22.14.0, npm y SonarScanner CLI. Ejecutarlo en la misma máquina que [SonarQube local](http://localhost:9000/projects).
- Usar los plugins de Pipeline declarativo, Git, JUnit y Credentials Binding. Guardar el token del proyecto de CI en Jenkins como **Secret text** con ID `sonarqube-softwaretextil`.
- El escaneo está activado de forma predeterminada. `SONAR_PROJECT_KEY` apunta por defecto a `softwaretextil-dev-ci`, la clave reservada para el job de `dev`. Preparar esa clave en SonarQube y usar un token con permiso de análisis sobre ella. Para la comparación histórica utilizar el [proyecto separado](http://localhost:9000/dashboard?id=softwaretextil-refactoring-compare).

## Etapas y evidencias

| Etapa | Verificación | Evidencia |
| --- | --- | --- |
| Construcción | Instala las dependencias bloqueadas y construye React con Vite. | Salida de Jenkins y distribución del frontend. |
| PostgreSQL de pruebas | Levanta un proyecto Compose por ejecución y toma el puerto asignado por Docker. | Contenedor saludable. Jenkins retira el contenedor y el volumen de pruebas de esa ejecución al terminar. |
| Pruebas automatizadas | Django verifica la configuración y las migraciones. Pytest y Node ejecutan sus suites. ESLint revisa el frontend. | JUnit de Python y Node, cobertura Python en XML y HTML, y LCOV del cliente HTTP. |
| Distribución verificable | Recolecta estáticos, crea el ZIP y su SHA-256 y comprueba una copia extraída. | ZIP y checksum archivados en Jenkins. |
| SonarQube y Quality Gate | Importa XML y LCOV y espera el resultado del Gate. Una falla del análisis o del Gate falla el job. | Consola de Jenkins y dashboard de SonarQube. |

Las etapas ejecutan la construcción y las pruebas una sola vez. La distribución se archiva como evidencia de construcción. `make check` sigue disponible como verificación estricta de Ruff. [Configuración del scanner y del Quality Gate](https://docs.sonarsource.com/sonarqube-server/2025.2/analyzing-source-code/ci-integration/overview).

Para obtener el antes y el después, sigue la [guía de reproducción](ejecucion-local.md). Guarda la evidencia del análisis de `dev` antes de enviar el análisis posterior a la misma clave.
