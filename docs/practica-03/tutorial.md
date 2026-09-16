# Tutorial de construcción automática de SoftwareTextil

## 1. Objetivo

La Práctica 03 pide describir y ejecutar la construcción del sistema mediante
una herramienta automática. SoftwareTextil usa **GNU Make** como punto de
entrada y conserva las herramientas propias de cada parte: `uv` para Python,
`npm ci` y Vite para React, Django para checks y estáticos, y un script Python
para producir y verificar el ZIP final.

Instalar dependencias, ejecutar el servidor y construir son operaciones
distintas. Python no genera aquí un ejecutable nativo: el entregable es una
distribución ZIP que requiere Python, sus dependencias y PostgreSQL.

## 2. Herramientas elegidas

| Herramienta | Función |
| --- | --- |
| GNU Make | Modela etapas, dependencias, orden y fallo inmediato. |
| uv | Selecciona Python 3.11, instala `uv.lock` y ejecuta herramientas Python. |
| npm | `npm ci` reproduce `package-lock.json`. |
| Vite | Compila React, CSS y HTML en `frontend/inventario/dist`. |
| Django | Comprueba configuración/migraciones y ejecuta `collectstatic`. |
| Ruff y pytest | Análisis estático, formato y pruebas Python. |
| Docker Compose | Prepara PostgreSQL 16 para las pruebas que requieren su semántica. |
| Python estándar | Genera ZIP, manifiesto y SHA-256 sin añadir otra dependencia. |

Maven y CMake son alternativas adecuadas para Java o C/C++; en este proyecto
añadirlos duplicaría la gestión que ya realizan uv, npm y Vite. Un pipeline de
CI tampoco es necesario para esta práctica local.

## 3. Entorno utilizado

La ejecución documentada se realizó en Linux Arch (`Linux 7.1.9-arch1-2`,
x86_64) el 16-09-2026. Versiones observadas:

- GNU Make 4.4.1.
- uv 0.9.10 y Python seleccionado 3.11.15 (`.python-version`: `3.11`).
- Node 26.7.0 y npm 12.0.2. El repositorio fija Node 22.14.0 como versión de
  referencia; ambas satisfacen Vite 7 (`^20.19.0 || >=22.12.0`).
- Vite 7.3.6 resuelto por `package-lock.json`.
- Docker 29.7.2 y Docker Compose 5.5.0; el daemon no estuvo disponible durante
  la verificación final.

## 4. Instalación y configuración en Arch Linux

Instalar las herramientas del sistema:

```bash
sudo pacman -S --needed git make nodejs npm docker docker-compose unzip
sudo systemctl enable --now docker
```

Instalar uv y Python 3.11:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.11
```

La versión concreta recomendada de Node está en `.node-version`. Si se usa un
gestor compatible con ese archivo, seleccionar `22.14.0`; Node 20.19 o cualquier
Node desde 22.12 también satisface el motor declarado por Vite 7.

Comprobar la instalación desde la raíz del repositorio:

```bash
make prerequisites
```

## 5. Clonado y rama

```bash
git clone https://github.com/javierRock/SoftwareTextil.git
cd SoftwareTextil
git switch doc/automatic
```

Todos los comandos restantes, salvo los que incluyen un `cd` explícito, se
ejecutan desde `SoftwareTextil/`.

## 6. Variables de entorno y PostgreSQL

Crear una configuración local sin versionar secretos:

```bash
cp .env.example .env
```

El ejemplo define `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y
`DJANGO_SECRET_KEY`. Sus valores son solo para desarrollo. El usuario de
PostgreSQL necesita permiso para crear la base temporal usada por pytest-django.

Iniciar la base y esperar su healthcheck:

```bash
docker compose up -d --wait db
docker compose ps
```

El build no ejecuta `migrate` ni genera migraciones. `makemigrations --check
--dry-run` solo detecta diferencias. Para ejecutar la aplicación por primera
vez se preparan las tablas de manera explícita:

```bash
uv run python manage.py migrate
```

## 7. Modelo de construcción

Los metadatos `[project]` de `pyproject.toml` definen `software-textil` versión
`0.1.0`. `[tool.software-textil.release]` define ZIP, directorio `dist/` y una
lista explícita de entradas. No se añadió un `build-system` porque `[tool.uv]
package = false` y no se promete un wheel instalable.

El `Makefile` serializa la ejecución con `.NOTPARALLEL` y usa Bash con
`-eu -o pipefail`. La cadena es:

```text
prerequisites → deps → frontend-check → frontend → check
             → db-ready → test → static → package → verify-release → build
```

Django usa `config.settings.build` para `collectstatic`, con `STATIC_ROOT` en
`build/staticfiles`; no se modifican los settings de producción. Vite conserva
la base `/static/zuren/` y produce `assets/app.js`.

## 8. Construcción paso a paso

Para observar cada etapa individualmente:

```bash
make deps
make frontend
make check
make test
make static
make package
make verify-release
```

Para el proceso completo:

```bash
make clean
make build
```

Make detiene el proceso en el primer error y no anuncia éxito ni conserva un
ZIP anterior como resultado nuevo. La preparación de PostgreSQL debe haberse
completado antes.

## 9. Visualización de resultados

Una construcción completa crea:

```text
dist/software-textil-0.1.0.zip
dist/software-textil-0.1.0.zip.sha256
```

Comprobar integridad e inventario:

```bash
cd dist
sha256sum -c software-textil-0.1.0.zip.sha256
unzip -l software-textil-0.1.0.zip
cd ..
```

`RELEASE-MANIFEST.json`, dentro del ZIP, registra proyecto, versión, commit,
estado del árbol, versiones de herramientas e inventario. La ejecución observó
380 entradas y comprobó que `.env`, `.git`, `.venv`, `node_modules`, `media/` y
`db.sqlite3` no estuvieran incluidos. El checksum prueba la integridad de ese
archivo concreto; no implica reproducibilidad byte a byte.

## 10. Extracción y ejecución

El ZIP ya contiene el frontend construido; Node no es necesario para ejecutarlo.

```bash
mkdir -p /tmp/software-textil-release
unzip dist/software-textil-0.1.0.zip -d /tmp/software-textil-release
cd /tmp/software-textil-release
cp .env.example .env
uv sync --locked --no-dev
uv run --locked --no-dev python manage.py check --settings=config.settings.build
uv run python manage.py migrate
uv run python manage.py runserver
```

PostgreSQL debe estar accesible según `.env`. Esta es una ejecución de
desarrollo; servir estáticos con `DEBUG=False` en producción requiere un
servidor o middleware de estáticos y queda fuera del alcance de la práctica.

## 11. Limpieza, reconstrucción y problemas frecuentes

```bash
make clean
make build
```

`clean` elimina solo `build/`, `frontend/inventario/dist/` y `dist/`; no toca
bases, volúmenes, archivos del usuario ni cambios Git.

- **Docker daemon no disponible:** iniciar `docker.service` y repetir `docker
  compose up -d --wait db`.
- **Base `software_textil` inexistente:** comprobar variables de `.env` y que
  el contenedor esté saludable.
- **Vite rechaza Node:** usar una versión que satisfaga `^20.19.0 || >=22.12.0`.
- **Ruff detiene el build:** corregir los errores reportados; no se deben omitir
  reglas ni reducir controles para obtener un resultado verde.
- **`npm ci` informa vulnerabilidades:** revisar `npm audit` por separado; no
  actualizar dependencias mayores automáticamente dentro de esta práctica.
- **pytest no puede crear su base:** conceder `CREATEDB` al usuario local de
  pruebas, nunca apuntar la suite a producción.

## 12. Archivos y documentación oficial

- [Makefile](../../Makefile)
- [Configuración Python y release](../../pyproject.toml)
- [Configuración Vite](../../frontend/inventario/vite.config.js)
- [Settings de construcción](../../config/settings/build.py)
- [Empaquetador](../../scripts/package_release.py)
- [Verificador](../../scripts/verify_release.py)
- [Evidencias](evidencias.md)
- [GNU Make](https://www.gnu.org/software/make/manual/)
- [uv: proyectos y sincronización](https://docs.astral.sh/uv/concepts/projects/sync/)
- [npm ci](https://docs.npmjs.com/cli/commands/npm-ci)
- [Vite: build de producción](https://vite.dev/guide/build.html)
- [Django: archivos estáticos](https://docs.djangoproject.com/en/5.2/howto/static-files/)
- [Docker Compose](https://docs.docker.com/compose/)
