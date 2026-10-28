# Práctica 03: construcción automática de SoftwareTextil

**Curso:** Ingeniería de Software II · **Tema:** Construcción automática  
**Repositorio base:** https://github.com/javierRock/SoftwareTextil  
**Revisión de origen:** `63e48ac75026d682c231efb724f436e265489653`  
**Rama preparada:** `codex/practica-3-construccion-automatica`

## 1. Qué se entrega y por qué se eligió esta herramienta

SoftwareTextil es una aplicación Python/Django con una interfaz React y una base PostgreSQL. La práctica menciona Maven y Gradle como ejemplos para Java, pero permite elegir una herramienta de construcción adecuada al lenguaje. Aquí se utiliza **GNU Make** como constructor automático: su archivo `Makefile` coordina las herramientas que ya utiliza el proyecto.

- **GNU Make:** declara tareas, dependencias y orden de ejecución; detiene el proceso ante un error.
- **uv:** instala Python 3.11 y las dependencias Python según `uv.lock`.
- **npm y Vite:** instalan las dependencias JavaScript del lockfile y generan la SPA de producción.
- **pytest y Node:** ejecutan las pruebas existentes.
- **Python/zipfile:** empaqueta las fuentes y la SPA compilada en un ZIP con un manifiesto SHA-256.
- **GitHub Actions:** ejecuta el mismo constructor al publicar cambios y conserva artefactos.

El entregable es `dist/software-textil-0.1.0.zip`. Es un paquete de aplicación con fuentes y frontend compilado; requiere los entornos y servicios descritos aquí para ejecutarse. El proyecto original declara `tool.uv.package = false`, por lo que se conserva su organización y no se inventa un paquete wheel incompleto.

## 2. Relación con los requisitos de la práctica

| Requisito del PDF | Implementación | Evidencia |
| --- | --- | --- |
| Instalar/configurar una herramienta | GNU Make + uv + Node/npm | Sección 3 |
| Información del proyecto: nombre, versión, tipo | `pyproject.toml`: `software-textil`, `0.1.0`; salida ZIP definida por `scripts/package_practica3.py` | Modelo y ZIP |
| Opciones de compilación | Python 3.11 en Make; validación de bytecode con `compileall`; Vite con `vite.config.js` | Log de construcción |
| Gestión de dependencias | `uv sync --locked`, `npm ci`; lockfiles originales | `uv.lock`, `package-lock.json` |
| Construir usando el modelo | `make verify` | `BUILD SUCCESS` y código de salida 0 |
| Visualizar resultados | ZIP, SPA y reporte JUnit | Secciones 5 y 6 |
| GitHub, commits y ramas | Rama local con commits; flujo CI preparado | Publicar siguiendo sección 8 |
| Tutorial de herramienta, instalación y construcción | Este documento | Tutorial completo |

## 3. Instalación de herramientas

Se necesita acceso a Internet para descargar runtimes, dependencias y la imagen PostgreSQL. Los comandos del tutorial se ejecutan en una terminal POSIX: Terminal en macOS, Bash en Linux o Ubuntu/WSL2 en Windows. Ejecutar `make` en PowerShell nativo no es el procedimiento soportado.

### macOS

1. Instalar las herramientas de línea de comandos de Apple si no están disponibles:

   ```bash
   xcode-select --install
   ```

   Proporcionan Git y GNU Make. Si ya están instaladas, continuar.

2. Instalar **Node.js 24 LTS** desde https://nodejs.org/en/download. La verificación local utilizó Node `24.19.0` y npm `11.6.2`. El instalador de Node incluye npm.
3. Instalar uv con el instalador oficial y volver a abrir la terminal:

   ```bash
   curl -LsSf https://astral.sh/uv/0.12.17/install.sh | sh
   ```

4. Instalar y abrir Docker Desktop desde https://docs.docker.com/desktop/setup/install/mac-install/.

### Linux y Windows mediante WSL2

En Windows, instalar Ubuntu con `wsl --install` desde PowerShell de administrador, completar la instalación y activar la integración de Ubuntu en Docker Desktop. Ejecutar el resto desde Ubuntu.

En Ubuntu:

```bash
sudo apt update
sudo apt install -y make git curl unzip
curl -LsSf https://astral.sh/uv/0.12.17/install.sh | sh
```

Cerrar y abrir la terminal. Instalar Node.js 24 desde las instrucciones oficiales de https://nodejs.org/en/download. En Linux configurar Docker Engine con el complemento Compose, o Docker Desktop. En WSL usar Docker Desktop con integración activada.

### Comprobación

```bash
git --version
make --version
uv --version
node --version
npm --version
docker compose version
docker info
```

Make debe ser GNU Make 3.81 o superior, Node debe ser de la rama 24 y Docker debe responder. `make install` descarga Python 3.11 automáticamente mediante uv; no hace falta activar manualmente un entorno virtual.

## 4. Abrir el proyecto preparado

**Con la carpeta entregada:** abrir una terminal dentro de `SoftwareTextil`, donde se encuentran `Makefile` y `manage.py`.

**Con el ZIP:** extraer `software-textil-0.1.0.zip` y entrar en `software-textil-0.1.0`. Incluye `BUILD-MANIFEST.json`, que permite volver a empaquetar sin `.git`.

**Con el respaldo Git:** desde la carpeta que contiene el archivo bundle:

```bash
git clone SoftwareTextil-practica3.bundle SoftwareTextil-restaurado
cd SoftwareTextil-restaurado
git switch codex/practica-3-construccion-automatica
```

**Desde GitHub, después de publicar la rama:**

```bash
git clone --branch codex/practica-3-construccion-automatica https://github.com/javierRock/SoftwareTextil.git
cd SoftwareTextil
```

Esta última instrucción solo funcionará cuando la rama se haya subido a ese repositorio. Si se publica en un fork, utilizar la URL del fork. Clonar únicamente la rama original no incluye los archivos de esta práctica.

## 5. Construcción automática paso a paso

Desde la raíz del proyecto:

```bash
make help
make db-up
make verify
```

`make db-up` crea una base **exclusiva para la práctica** con PostgreSQL 16, espera a que esté lista y utiliza el puerto local `55432`. No requiere copiar `.env`: Make exporta los valores de desarrollo de la práctica.

`make verify` ejecuta, en orden:

1. `uv sync --locked --python 3.11`: crea `.venv` y valida/instala el lockfile sin actualizarlo.
2. `npm --prefix frontend/inventario ci`: instala las versiones resueltas en `package-lock.json`.
3. `npm --prefix frontend/inventario run build`: Vite transforma React/JSX y genera HTML, CSS y JavaScript de producción.
4. `python -m compileall -q apps config manage.py`: valida la compilación de los módulos Python a bytecode. Python no genera un ejecutable nativo; los `.pyc` son locales y no se incluyen en el ZIP.
5. `manage.py check --fail-level WARNING` y `makemigrations --check --dry-run`: revisan Django y la correspondencia de modelos/migraciones.
6. `pytest --junitxml=build/reports/pytest.xml`: ejecuta la suite sobre PostgreSQL, incluida la semántica de transacciones y bloqueos.
7. `npm test` y `npm run lint`: prueban el cliente HTTP y revisan JavaScript/React.
8. `scripts/package_practica3.py`: genera ZIP, manifiesto y checksum.
9. Muestra `BUILD SUCCESS` únicamente si todos esos pasos terminaron correctamente.

Para conservar tu propia evidencia en Bash o Zsh:

```bash
mkdir -p build/reports
set -o pipefail
make verify 2>&1 | tee build/reports/mi-construccion.log
```

`pipefail` permite conservar el fallo de Make aunque `tee` escriba correctamente el log.

### Archivos de configuración que se deben explicar

| Archivo | Responsabilidad |
| --- | --- |
| `Makefile` | Modelo principal: tareas, dependencias entre etapas, herramientas, versión Python y entorno de pruebas |
| `pyproject.toml` | Nombre, versión, Python mínimo, bibliotecas Python y configuración de pytest/Ruff |
| `uv.lock` | Versiones exactas y hashes de las dependencias Python |
| `.python-version` | Python 3.11 para ejecución con uv |
| `frontend/inventario/package.json` | Bibliotecas React, herramientas y scripts frontend |
| `frontend/inventario/package-lock.json` | Resolución exacta de dependencias JavaScript |
| `frontend/inventario/vite.config.js` | Base `/static/zuren/`, nombres de salida y compilación de React |
| `compose.practica3.yml` | PostgreSQL 16, volumen persistente y comprobación de disponibilidad |
| `.github/workflows/practica3.yml` | Ejecución del mismo modelo en GitHub Actions |

Ejemplo central del modelo:

```make
build: install frontend
	$(UV) run --locked python -m compileall -q apps config manage.py

verify: build check test package
	@echo 'BUILD SUCCESS: construccion, verificaciones, pruebas y ZIP completos.'
```

Las recetas llevan **tabulador**, no espacios. `.NOTPARALLEL` evita ejecutar estas etapas simultáneamente aunque se pase `-j`. Los objetivos son `.PHONY`: se repiten cuando se solicitan, en lugar de usar un resultado anterior como prueba de éxito.

`make build` construye sin pruebas; `make package` empaqueta lo que ya está construido. Para acreditar la práctica se usa **`make verify`**, no solo esos objetivos parciales. Ruff global se documenta como diagnóstico separado porque el repositorio base tiene observaciones previas; no forma parte del éxito declarado por `verify`.

## 6. Ver resultados y ejecutar la aplicación

```bash
ls -lh dist/
cat dist/software-textil-0.1.0.zip.sha256
ls frontend/inventario/dist/
```

Resultados:

- `dist/software-textil-0.1.0.zip`: fuentes versionadas, documentación y SPA compilada.
- `dist/software-textil-0.1.0.zip.sha256`: checksum del ZIP.
- `BUILD-MANIFEST.json` dentro del ZIP: revisión Git, estado de cambios locales, lista de fuentes y SHA-256 por archivo.
- `frontend/inventario/dist/index.html` y `assets/`: salida Vite.
- `build/reports/pytest.xml`: reporte de pruebas JUnit.

Para comprobar el checksum en macOS:

```bash
cd dist
shasum -a 256 -c software-textil-0.1.0.zip.sha256
cd ..
```

En Linux usar `sha256sum -c` en lugar de `shasum -a 256 -c`.

Para abrir la aplicación con datos de demostración:

```bash
make demo
make run
```

Abrir http://127.0.0.1:8000/. Usuarios de demostración del repositorio: `admin`, `inventario`, `cliente`, contraseña `Zuren2026!`, exclusivamente para la demostración local. `make demo` aplica las migraciones y el sembrador existente; la construcción no depende de estos registros de demostración.

Detener el servidor con Ctrl+C. Detener la base con `make db-down`; conserva el volumen. `make clean` elimina únicamente `build`, `dist` y la SPA generada; para recuperarlos repetir `make verify`.

## 7. Qué contiene el respaldo

Se conservan todos los archivos versionados del proyecto: backend, frontend, tests, migraciones, documentación, figuras UML y archivos de la práctica. También se incluye la SPA compilada. Se excluyen `.venv`, `node_modules`, secretos `.env`, bases de datos, archivos subidos a `media` y cachés. Las dependencias se recuperan mediante los lockfiles.

En un clon Git, el empaquetador usa `git ls-files`: **los archivos nuevos deben agregarse con `git add`** para formar parte del paquete. Los cambios de archivos ya versionados sí se incluyen, y el manifiesto indica si el árbol tenía cambios. Se recomienda realizar el commit y volver a ejecutar `make package` para obtener un respaldo asociado a un árbol limpio.

El ZIP conserva el código pero no el historial. `SoftwareTextil-practica3.bundle` conserva los objetos y referencias Git descargados, además de la rama y commits de esta práctica. El bundle se restaura con `git clone` y no depende de que GitHub esté disponible. No es una copia de issues, PR ni configuraciones de la plataforma.

## 8. Publicar la evidencia en GitHub

Los cambios están preparados localmente. **No se han publicado ni se ha ejecutado Actions en GitHub.**

Desde el clon entregado:

```bash
git status
git branch --show-current
git log --oneline -4
```

Si realizas nuevos cambios, confirma tu identidad Git, agrega únicamente los archivos de la práctica que corresponda y crea un commit. Los commits ya entregados no necesitan repetirse.

Con permiso de escritura en el repositorio original:

```bash
git push -u origin codex/practica-3-construccion-automatica
```

Sin permiso, crea un fork en GitHub y agrega su remoto, reemplazando `TU_USUARIO`:

```bash
git remote add entrega https://github.com/TU_USUARIO/SoftwareTextil.git
git push -u entrega codex/practica-3-construccion-automatica
```

Si restauraste el bundle, `origin` apunta al archivo local: agrega un remoto HTTPS llamado `entrega` y publica allí. Abrir luego **Actions → Practica 03 - Construccion automatica**. El workflow usa Ubuntu, Node, uv y un servicio PostgreSQL 16; ejecuta `make verify` y conserva el reporte y el ZIP como artefactos. En CI el puerto se cambia a `5432` mediante variables de entorno.

Para cerrar la entrega académica, adjuntar el enlace a la rama/commit publicado y, una vez que ocurra, el enlace a la ejecución satisfactoria de Actions. Las evidencias locales no se deben presentar como una ejecución remota.

## 9. Evidencias y guion breve de exposición

Las evidencias reales de esta preparación están en `evidencias/`, junto a este tutorial. El archivo `RESULTADOS.md` explica sus resultados y límites.

Capturas sugeridas para tu propia entrega:

1. Versiones de las herramientas y rama activa.
2. `Makefile` y metadatos de `pyproject.toml`.
3. Consola con `make verify`, resultados de pruebas y `BUILD SUCCESS`.
4. ZIP generado, checksum y SPA.
5. Aplicación abierta tras `make demo` y `make run`.
6. Rama/commits y Actions en GitHub después de publicar.

Guion: «Elegí GNU Make porque el proyecto combina Django y React. El modelo declara las tareas y coordina uv, npm/Vite y pytest. Las dependencias se instalan desde lockfiles. La validación usa PostgreSQL real. Una única orden construye, prueba y empaqueta; si un paso falla, el proceso se detiene. El ZIP guarda las fuentes y el frontend compilado y el bundle conserva el historial Git».

## 10. Problemas frecuentes

| Síntoma | Solución |
| --- | --- |
| `make: command not found` | Instalar GNU Make; en Windows ejecutar dentro de WSL2 |
| `uv` o `npm` no encontrado | Reabrir terminal y verificar PATH y las instalaciones de sección 3 |
| Docker no responde | Abrir Docker Desktop; revisar `docker info` |
| Puerto 55432 ocupado | Ejecutar `make db-up DB_PORT=55433` y usar `DB_PORT=55433` también en `verify`, `demo`, `run` y `db-down` |
| Error de conexión PostgreSQL | Ejecutar `make db-up` y revisar `docker compose -p softwaretextil-practica3 -f compose.practica3.yml ps` |
| Fallo de `uv sync --locked` o `npm ci` | Restaurar los lockfiles coherentes; si cambias dependencias intencionalmente, regenerar y versionar el lockfile correspondiente |
| No aparece un archivo nuevo en el ZIP | Ejecutar `git add ruta/del/archivo` antes de empaquetar |
| `missing separator` en Make | Sustituir la indentación de recetas por tabuladores |
| La web no muestra React | Ejecutar `make build`, luego `make run`; el HTML necesita el servidor Django |
| Hay avisos npm o Ruff | Consultar `RESULTADOS.md`; no confundir construcción exitosa con auditoría de seguridad o calidad totalmente limpia |

## 11. Referencias

- Enunciado proporcionado: `Pr_3_Automatic_Build.pdf`, actividades y entregables de la práctica 03.
- Repositorio y organización real: https://github.com/javierRock/SoftwareTextil
- GNU Make: https://www.gnu.org/software/make/manual/
- Instalación de uv: https://docs.astral.sh/uv/getting-started/installation/
- Dependencias bloqueadas con uv: https://docs.astral.sh/uv/concepts/projects/sync/
- `npm ci`: https://docs.npmjs.com/cli/v11/commands/npm-ci/
- Construcción Vite: https://vite.dev/guide/build
- uv en GitHub Actions: https://docs.astral.sh/uv/guides/integration/github/
