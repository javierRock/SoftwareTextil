SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.NOTPARALLEL:

FRONTEND_DIR := frontend/inventario
BUILD_SETTINGS := config.settings.build
DEV_SETTINGS := config.settings.dev
QUALITY_COMPOSE := docker compose -p softwaretextil-quality -f compose.quality.yml
export DB_NAME ?= software_textil_quality
export DB_USER ?= postgres
export DB_PASSWORD ?= postgres
export DB_HOST ?= 127.0.0.1
export DB_PORT ?= 55432

.PHONY: help prerequisites deps db-up db-down db-ready frontend-check frontend frontend-build check django-check test quality reportes frontend-reportes static collect-static invalidate-release package release-zip verify-release release-verify build clean

help: ## Muestra los objetivos disponibles.
	@awk 'BEGIN {FS = ":.*## "; printf "Uso: make <objetivo>\n\n"} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

prerequisites: ## Comprueba las herramientas requeridas.
	@command -v uv >/dev/null || { echo "Error: instala uv (https://docs.astral.sh/uv/)." >&2; exit 1; }
	@command -v npm >/dev/null || { echo "Error: instala Node.js $(shell cat .node-version) y npm." >&2; exit 1; }
	@command -v git >/dev/null || { echo "Error: instala Git para generar el manifiesto." >&2; exit 1; }
	@node -e 'const [major, minor] = process.versions.node.split(".").map(Number); const compatible = (major === 20 && minor >= 19) || (major === 22 && minor >= 12) || major > 22; if (!compatible) { console.error("Error: Vite requiere Node ^20.19.0 o >=22.12.0; versión actual: " + process.version); process.exit(1); }'
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

db-up: ## Levanta la base aislada para calidad y pruebas.
	$(QUALITY_COMPOSE) up -d --wait db

db-down: ## Detiene la base aislada para calidad y pruebas.
	$(QUALITY_COMPOSE) down

frontend-check: deps ## Ejecuta pruebas y lint del frontend.
	npm --prefix $(FRONTEND_DIR) test
	npm --prefix $(FRONTEND_DIR) run lint

frontend: frontend-check frontend-build ## Valida el frontend y construye la SPA.

frontend-build: ## Construye la SPA desde las dependencias instaladas.
	npm --prefix $(FRONTEND_DIR) run build

check: frontend ## Ejecuta análisis estático y checks de Django/migraciones.
	uv run --locked ruff check .
	uv run --locked ruff format --check .
	$(MAKE) django-check

django-check: ## Comprueba la configuración y migraciones de Django.
	DJANGO_SETTINGS_MODULE=$(BUILD_SETTINGS) uv run --locked python manage.py check
	DJANGO_SETTINGS_MODULE=$(BUILD_SETTINGS) uv run --locked python manage.py makemigrations --check --dry-run

test: check db-ready ## Ejecuta la suite Python contra PostgreSQL.
	uv run --locked pytest

quality: ## Ejecuta la suite completa, cobertura de pagos y reportes JUnit/XML.
	$(QUALITY_COMPOSE) up -d --wait db
	mkdir -p build/reports
	uv run --locked pytest --cov=apps/ventas/pagos --cov-branch --cov-report=term-missing --cov-report=xml:build/reports/coverage-quality.xml --junitxml=build/reports/pytest-quality-full.xml

reportes: ## Ejecuta la suite y genera reportes JUnit, cobertura HTML/XML (sin Docker; usa DB_PORT=5432 en local).
	mkdir -p build/reports
	uv run --locked pytest --cov --cov-report=term --cov-report=html --cov-report=xml --junitxml=build/reports/junit.xml

frontend-reportes: ## Ejecuta la suite Node y genera JUnit y LCOV para CI.
	mkdir -p build/reports
	node --experimental-test-coverage --test-coverage-include='$(FRONTEND_DIR)/src/services/api.js' \
		--test-reporter=spec --test-reporter-destination=stdout \
		--test-reporter=junit --test-reporter-destination=build/reports/node-junit.xml \
		--test-reporter=lcov --test-reporter-destination=build/reports/frontend-lcov.info \
		--test $(FRONTEND_DIR)/src/services/*.test.js

static: test collect-static ## Valida y recolecta archivos estáticos.

collect-static: ## Recolecta los estáticos después de construir la SPA.
	rm -rf build/staticfiles
	DJANGO_SETTINGS_MODULE=$(BUILD_SETTINGS) uv run --locked python manage.py collectstatic --noinput --clear

invalidate-release:
	@rm -f dist/*.zip dist/*.zip.sha256

package: invalidate-release static release-zip ## Valida y genera el ZIP con su manifiesto y checksum.

release-zip: ## Empaqueta los archivos construidos y genera el checksum.
	uv run --locked python -m scripts.package_release

verify-release: package release-verify ## Construye y verifica la distribución.

release-verify: ## Verifica el ZIP existente desde una extracción temporal.
	uv run --locked python -m scripts.verify_release

build: verify-release ## Ejecuta el proceso completo de construcción automática.
	@echo "Construcción completada. Artefactos disponibles en dist/."

clean: ## Elimina únicamente salidas generadas por la construcción.
	rm -rf build frontend/inventario/dist dist
