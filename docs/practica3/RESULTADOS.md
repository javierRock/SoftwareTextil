# Resultados de la práctica 03

Verificación local realizada el **21 de septiembre de 2026 (America/Lima)** sobre la revisión original `63e48ac75026d682c231efb724f436e265489653`, con los archivos de construcción añadidos en la rama `codex/practica-3-construccion-automatica`.

## Resultados ejecutados

| Verificación | Resultado | Evidencia |
| --- | --- | --- |
| Instalación Python desde lockfile | Correcta, Python 3.11.16 y uv 0.12.17 | `evidencias/construccion-local.txt` |
| Instalación JavaScript con npm ci | Correcta, Node 24.19.0 / npm 11.6.2 | Log de construcción |
| Vite | Correcta, Vite 7.3.6; 55 módulos transformados | Log de construcción |
| Compilación de módulos Python | Correcta | Log de construcción |
| Django check | Sin incidencias | Log de construcción |
| Migraciones pendientes | No hay cambios pendientes | Log de construcción |
| pytest sobre PostgreSQL 16 | **271 aprobadas** | `evidencias/pytest.xml` |
| Pruebas JavaScript | **4 aprobadas** | Log de construcción |
| ESLint frontend | Correcto | Log de construcción |
| Empaquetado inicial | ZIP generado y SHA-256 calculado | Log de construcción |
| Migraciones y datos de demostración | Correctos | `evidencias/demo.txt` |
| HTTP con servidor Django real | `/`, `/login`, JS y CSS responden 200 | `evidencias/smoke-http.txt` |
| Ruff del nuevo empaquetador | Sin incidencias | `uv run --locked ruff check scripts/package_practica3.py` |

El log de construcción documenta la primera ejecución completa, anterior a incorporar este tutorial y las evidencias al ZIP. Su checksum corresponde a ese paquete inicial. El ZIP de entrega se vuelve a empaquetar después del commit final; **el checksum válido para la entrega es el archivo `.sha256` adyacente**, y su manifiesto identifica la revisión exacta.

## Hallazgos previos conservados

- Ruff global reporta **58 observaciones en código preexistente**. Se guardó la salida en `evidencias/ruff-diagnostico.txt`. No se modificaron reglas ni módulos de negocio para ocultarlas. La ejecución de Ruff global no es una condición de `make verify`; sí lo son las verificaciones Django, pruebas y ESLint descritas.
- `npm audit` reporta **5 vulnerabilidades de severidad alta** en el árbol de dependencias instalado. El detalle real queda en `evidencias/npm-audit.json`. Se conservaron las dependencias originales para esta práctica de construcción; resolver las alertas requiere evaluar y probar las actualizaciones correspondientes.
- `make verify` demuestra construcción y pruebas exitosas, no certifica que no existan vulnerabilidades ni que toda la aplicación tenga cobertura del 100 %.
- Las pruebas HTTP verifican entrega de HTML y archivos compilados; no constituyen una prueba visual ni un recorrido completo del navegador.

## Alcance y pendientes de publicación

La rama y los commits son locales. **No se ejecutó `git push` ni GitHub Actions**. El tutorial explica cómo publicar en el repositorio original con permiso o en un fork. La ejecución remota y sus enlaces quedan por generar después de publicar.

El ZIP contiene el proyecto y la SPA; el bundle conserva el historial Git descargado y los commits de la práctica. No se incluyen secretos locales, archivos de usuarios ni un volcado de base de datos. Los registros de ejemplo se recrean con `make demo`. La base de práctica utiliza un volumen separado y el puerto 55432.

Las pruebas locales se ejecutaron en macOS ARM64. El workflow para Ubuntu y las instrucciones WSL están preparados, pero no se presentan como ejecutados en esas plataformas.
