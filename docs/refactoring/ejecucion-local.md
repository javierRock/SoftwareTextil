# Revisión y reproducción local

Ejecuta los comandos desde la raíz de tu copia de SoftwareTextil.
Rama: `refactor/code-quality`. Base: `a312d0a`. Todo el trabajo permanece local hasta su aprobación.

## Preparar entorno

```bash
uv sync --frozen
docker compose -p textil-quality -f compose.quality.yml up -d db
DB_PORT=55432 DB_NAME=software_textil_quality uv run pytest --cov=apps --cov-report=xml --cov-report=html --junitxml=build/reports/junit.xml
SONAR_LOCAL_PORT=9008 docker compose -p textil-refactoring-expanded -f compose.sonar.yml up -d
```

SonarQube local en http://127.0.0.1:9008. Usa las credenciales de tu instancia local.
El servidor utiliza la imagen nativa arm64 disponible para este equipo. El scanner 5.0.1 puede requerir emulación amd64.

## Ejecutar análisis

Esperar a que `/api/system/status` muestre `UP`. Ejecutar desde la raíz del código que se desea analizar:

```bash
docker run --rm --platform linux/amd64 \
  -v "$PWD:/usr/src" \
  -e SONAR_HOST_URL=http://host.docker.internal:9008 \
  sonarsource/sonar-scanner-cli:5.0.1 \
  -Dsonar.login=admin -Dsonar.password=admin \
  -Dsonar.qualitygate.wait=true
```

Si se cambió la contraseña, usar las credenciales locales vigentes sin guardarlas en Git. Un Quality Gate fallido no significa que el análisis no se haya procesado; revisar el resultado del servidor.

Extrae el commit base `a312d0a` en un directorio aparte y copia allí `sonar-project.properties`. Analiza primero esa copia, exporta los resultados y luego analiza el código refactorizado.

Antes del scanner, generar los archivos de cobertura desde cada copia. El XML usa la ruta que verá el contenedor. El LCOV cubre el cliente HTTP que ejecutan las pruebas Node.

```bash
python3 -c "import xml.etree.ElementTree as E; t=E.parse('build/reports/coverage.xml'); [setattr(s,'text','/usr/src/apps') for s in t.findall('./sources/source')]; t.write('build/reports/sonar-coverage.xml')"
node --experimental-test-coverage --test-coverage-include='frontend/inventario/src/services/api.js' --test-reporter=lcov --test-reporter-destination=build/reports/frontend-lcov.info --test frontend/inventario/src/services/*.test.js
```

La cobertura de SonarQube usa un alcance mayor que pytest-cov. Ejecuta los dos análisis sobre copias limpias, con la misma configuración y sin dependencias ni builds dentro de las carpetas analizadas.

```bash
python3 scripts/quality_snapshot.py docs/refactoring/evidencias/ampliada/antes/sonarqube-comparable
# Después del análisis del código modificado:
python3 scripts/quality_snapshot.py docs/refactoring/evidencias/ampliada/despues/sonarqube-comparable
```

El exportador pagina todos los issues y conserva métricas, Quality Gate e historial. No modifica issues. Los análisis deben usar el mismo perfil y exclusiones.

## Publicación posterior a revisión

1. Revisar matriz, diff, pruebas y ambos análisis reales.
2. Crear/actualizar GitHub Issues y tablero con responsables confirmados, usando los identificadores Q como referencia local.
3. Enlazar los commits locales a los issues reales en la descripción del PR.
4. Hacer push y abrir PR hacia `dev`; completar validación y revisión antes de integrar.
5. La integración a `dev` y cualquier despliegue a producción son pasos posteriores independientes.

Las URLs de tareas y commits remotos solo podrán completarse al publicar. El Kanban local no equivale a un GitHub Project creado.
