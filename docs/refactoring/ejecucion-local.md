# Revisión y reproducción local

Ejecuta los comandos desde la raíz de tu copia de SoftwareTextil.
La comparación publicada usa `a312d0a` de `dev` y el código de `7785a6a` en `refactor/code-quality`.

## Preparar entorno

```bash
mkdir -p build/reports
uv sync --frozen
docker compose -p textil-quality -f compose.quality.yml up -d db
DB_PORT=55432 DB_NAME=software_textil_quality uv run pytest --cov=apps --cov-report=xml --cov-report=html --junitxml=build/reports/junit.xml
SONAR_LOCAL_PORT=9008 docker compose -p textil-refactoring-expanded -f compose.sonar.yml up -d
```

SonarQube local en http://127.0.0.1:9008. Usa las credenciales de tu instancia local.
El servidor usa SonarQube 9.9.7 Community. Si el primer inicio de sesión exige cambiar la contraseña inicial, el dueño debe completar ese paso en la interfaz.

## Ejecutar análisis

Prepara dos copias limpias de `a312d0a` y `7785a6a`. Copia `sonar-project.properties` de la segunda a la primera. Si la instancia ya contiene evidencia histórica, usa la misma clave nueva en las dos copias y pasa esa clave al exportador mediante `--project`. Analiza primero la base, guarda las capturas y exporta su resultado antes de ejecutar el análisis posterior.

Antes del scanner, generar los archivos de cobertura desde cada copia. El XML usa la ruta que verá el contenedor. El LCOV cubre el cliente HTTP que ejecutan las pruebas Node. Usa Node 22.14.0 en ambas copias.

```bash
python3 -c "import xml.etree.ElementTree as E; t=E.parse('build/reports/coverage.xml'); [setattr(s,'text','/usr/src/apps') for s in t.findall('./sources/source')]; t.write('build/reports/sonar-coverage.xml')"
node --experimental-test-coverage --test-coverage-include='frontend/inventario/src/services/api.js' --test-reporter=lcov --test-reporter-destination=build/reports/frontend-lcov.info --test frontend/inventario/src/services/*.test.js
```

Espera a que `/api/system/status` muestre `UP`. En Linux, con un token de análisis cargado en `SONAR_LOGIN`, ejecuta el scanner desde la raíz de cada copia:

```bash
docker run --rm --platform linux/amd64 --network host \
  -v "$PWD:/usr/src" \
  -e SONAR_HOST_URL=http://127.0.0.1:9008 -e SONAR_LOGIN \
  sonarsource/sonar-scanner-cli:5.0.1 \
  -Dsonar.qualitygate.wait=true
```

Conserva el token fuera de Git. Consulta la [documentación de SonarScanner para SonarQube 9.9](https://docs.sonarsource.com/sonarqube-server/9.9/analyzing-source-code/scanners/sonarscanner). Si el scanner devuelve un error de Quality Gate, comprueba en el servidor que el análisis se procesó.

La cobertura de SonarQube usa un alcance mayor que pytest-cov. Ejecuta los dos análisis sobre copias limpias, con la misma configuración y sin dependencias ni builds dentro de las carpetas analizadas.

```bash
SONAR_EVIDENCIAS="$(mktemp -d)"
python3 scripts/quality_snapshot.py "$SONAR_EVIDENCIAS/antes"
# Después del análisis del código modificado, desde la misma sesión de shell:
python3 scripts/quality_snapshot.py "$SONAR_EVIDENCIAS/despues"
```

Ejecuta el exportador desde la rama de trabajo. Carga las credenciales locales de lectura mediante `SONAR_USER` y `SONAR_PASSWORD`. El exportador pagina todos los issues y conserva métricas, Quality Gate e historial. Los análisis deben usar el mismo perfil y exclusiones.

## Revisión en GitHub

Consulta el [PR #46](https://github.com/javierRock/SoftwareTextil/pull/46) hacia `dev` y el [índice de trazabilidad](trazabilidad.md). La revisión de los criterios de aceptación y la integración en `dev` preceden a cualquier despliegue.
