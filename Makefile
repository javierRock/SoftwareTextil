SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.NOTPARALLEL:

FRONTEND_DIR := frontend/inventario
BUILD_SETTINGS := config.settings.build
DEV_SETTINGS := config.settings.dev

.PHONY: help prerequisites deps db-ready frontend-check frontend check test static invalidate-release package verify-release build clean

help: ## Muestra los objetivos disponibles.
	@awk 'BEGIN {FS = ":.*## "; printf "Uso: make <objetivo>\n\n"} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

prerequisites: ## Comprueba las herramientas requeridas.
	@command -v uv >/dev/null || { echo "Error: instala uv (https://docs.astral.sh/uv/)." >&2; exit 1; }
	@command -v npm >/dev/null || { echo "Error: instala Node.js $(shell cat .node-version) y npm." >&2; exit 1; }
	@command -v git >/dev/null || { echo "Error: instala Git para generar el manifiesto." >&2; exit 1; }
	@node -e 'const [major, minor] = process.versions.node.split(".").map(Number); if (!((major === 20 && minor >= 19) || major >= 22)) { console.error("Error: Vite requiere Node ^20.19.0 o >=22.12.0; versión actual: " + process.version); process.exit(1); }'
	@printf 'Make: '; make --version | sed -n '1p'
	@uv --version
	@printf 'Python seleccionado: '; uv run --no-sync python --version
	@printf 'Node: '; node --version
	@printf 'npm: '; npm --version

deps: prerequisites ## Instala dependencias bloqueadas de Python y frontend.
	uv sync --locked
	npm --prefix $(FRONTEND_DIR) ci

db-ready: deps ## Comprueba la conexión PostgreSQL usada por las pruebas.
	@DJANGO_SETTINGS_MODULE=$(DEV_SETTINGS) uv run --locked python -c 'from django.db import connection; connection.ensure_connection(); print("PostgreSQL disponible para pruebas.")' || { echo "Error: PostgreSQL no está disponible. Ejecuta 'docker compose up -d db' y espera a que esté saludable." >&2; exit 1; }

frontend-check: deps ## Ejecuta pruebas y lint del frontend.
	npm --prefix $(FRONTEND_DIR) test
	npm --prefix $(FRONTEND_DIR) run lint

frontend: frontend-check ## Construye la SPA con Vite.
	npm --prefix $(FRONTEND_DIR) run build

check: frontend ## Ejecuta análisis estático y checks de Django/migraciones.
	uv run --locked ruff check .
	uv run --locked ruff format --check .
	DJANGO_SETTINGS_MODULE=$(BUILD_SETTINGS) uv run --locked python manage.py check
	DJANGO_SETTINGS_MODULE=$(BUILD_SETTINGS) uv run --locked python manage.py makemigrations --check --dry-run

test: check db-ready ## Ejecuta la suite Python contra PostgreSQL.
	uv run --locked pytest

static: test ## Recolecta archivos estáticos en build/staticfiles.
	rm -rf build/staticfiles
	DJANGO_SETTINGS_MODULE=$(BUILD_SETTINGS) uv run --locked python manage.py collectstatic --noinput --clear

invalidate-release:
	@rm -f dist/*.zip dist/*.zip.sha256

package: invalidate-release static ## Genera el ZIP, manifiesto y checksum SHA-256.
	uv run --locked python -m scripts.package_release

verify-release: package ## Verifica checksum, contenido y ejecución desde una extracción temporal.
	uv run --locked python -m scripts.verify_release

build: verify-release ## Ejecuta el proceso completo de construcción automática.
	@echo "Construcción completada. Artefactos disponibles en dist/."

clean: ## Elimina únicamente salidas generadas por la construcción.
	rm -rf build frontend/inventario/dist dist
