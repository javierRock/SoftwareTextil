# Revisión y reproducción local

La [comparación publicada](resultado-ampliado.md) se ejecutó con SonarQube 9.9.7 y SonarScanner 5.0.1. Compara `a312d0a` de `dev` con el código de `7785a6a` en `refactor/code-quality`.

La instancia activa de esta máquina es [SonarQube Community Build en localhost:9000](http://localhost:9000/projects). El proyecto [SoftwareTextil](http://localhost:9000/dashboard?id=software-textil) conserva su análisis previo. Para repetir la comparación, usa [SoftwareTextil - Comparacion de refactorizacion](http://localhost:9000/dashboard?id=softwaretextil-refactoring-compare) o una clave nueva si ese proyecto ya tiene una comparación que deseas conservar. Registra la versión de la instancia junto con los resultados de la reproducción.

## Preparar las dos copias

Desde la raíz de SoftwareTextil, extrae los dos commits en directorios nuevos. Copia la configuración de Sonar de la segunda copia a la primera.

```bash
SONAR_COPIAS="$(mktemp -d)"
mkdir -p "$SONAR_COPIAS/antes" "$SONAR_COPIAS/despues"
git archive a312d0a | tar -x -C "$SONAR_COPIAS/antes"
git archive 7785a6a | tar -x -C "$SONAR_COPIAS/despues"
cp "$SONAR_COPIAS/despues/sonar-project.properties" "$SONAR_COPIAS/antes/"
```

Configura la misma clave y el mismo nombre de proyecto en ambos archivos `sonar-project.properties`. Usa la misma configuración de exclusiones y los mismos perfiles de calidad para los dos análisis. El proyecto de comparación usa **Previous version** como definición de código nuevo.

Levanta PostgreSQL aislado desde una de las copias. Si el puerto 55432 está ocupado, elige otro puerto y úsalo también para pytest.

```bash
docker compose -p textil-quality -f "$SONAR_COPIAS/despues/compose.quality.yml" up -d --wait db
```

Genera la cobertura en cada copia con Python 3.11 y Node 22.14.0. Ejecuta lo siguiente desde la raíz de cada una.

```bash
mkdir -p build/reports
uv sync --frozen
DB_PORT=55432 DB_NAME=software_textil_quality uv run --no-sync pytest --cov=apps --cov-report=xml:build/reports/coverage.xml
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET

report = ET.parse("build/reports/coverage.xml")
for source in report.findall("./sources/source"):
    source.text = str(Path("apps").resolve())
report.write("build/reports/sonar-coverage.xml")
PY
node --experimental-test-coverage --test-coverage-include='frontend/inventario/src/services/api.js' --test-reporter=lcov --test-reporter-destination=build/reports/frontend-lcov.info --test frontend/inventario/src/services/*.test.js
```

## Analizar y exportar

Comprueba que [el estado del servidor](http://localhost:9000/api/system/status) indique `UP`. Usa un token con permiso de análisis sobre el proyecto de comparación en la variable de entorno local `SONAR_TOKEN`. Conserva el token fuera de Git. Ejecuta con SonarScanner CLI desde la raíz de la primera copia.

```bash
SONAR_HOST_URL=http://localhost:9000 sonar-scanner -Dsonar.qualitygate.wait=true
```

1. Captura en el dashboard el nombre del proyecto, fecha y resultado de la línea base. Exporta el análisis, métricas, issues y Gate desde la [Web API de la instancia](http://localhost:9000/web_api), con una sesión autenticada. Usa los endpoints `api/project_analyses/search`, `api/measures/component`, `api/issues/search` y `api/qualitygates/project_status`. Guarda las exportaciones y el log del scanner en una carpeta nueva.
2. Ejecuta el mismo comando desde la segunda copia. Si el scanner devuelve un error de Quality Gate, comprueba en SonarQube que el análisis se procesó.
3. Captura y exporta el resultado posterior. En la vista de código nuevo registra el valor y umbral de la condición de cobertura. Indica la fecha y versión de SonarQube al presentar estas nuevas evidencias.

## Revisión en GitHub

Consulta el [PR #46](https://github.com/javierRock/SoftwareTextil/pull/46) hacia `dev` y el [índice de trazabilidad](trazabilidad.md). La revisión de los criterios de aceptación y la integración en `dev` preceden a cualquier despliegue.
