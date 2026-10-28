# Practica 03: modelo de construccion para GNU Make 3.81 o superior.
# Ejecutar desde la raiz. Las recetas requieren un shell POSIX (WSL en Windows).
.DEFAULT_GOAL := help
.NOTPARALLEL:
.PHONY: help install db-up db-down frontend check test lab05 build package verify demo run clean

UV ?= uv
NPM ?= npm
FRONTEND := frontend/inventario
COMPOSE_PROJECT ?= softwaretextil-practica3
COMPOSE := docker compose -p $(COMPOSE_PROJECT) -f compose.practica3.yml
export DB_NAME ?= software_textil_practica3
export DB_USER ?= postgres
export DB_PASSWORD ?= postgres
export DB_HOST ?= 127.0.0.1
export DB_PORT ?= 55432
export DJANGO_SETTINGS_MODULE := config.settings.dev

help:
	@echo 'make db-up     PostgreSQL 16 aislado para la practica'
	@echo 'make verify    Instalar, construir, verificar, probar y empaquetar'
	@echo 'make build     Construir sin ejecutar pruebas (no es verificacion completa)'
	@echo 'make demo      Migrar y cargar datos de demostracion'
	@echo 'make run       Servidor local en http://127.0.0.1:8000'
	@echo 'make db-down   Detener la base de la practica conservando sus datos'
	@echo 'make clean     Borrar solo salidas generadas de construccion'

install:
	$(UV) sync --locked --python 3.11
	$(NPM) --prefix $(FRONTEND) ci

db-up:
	$(COMPOSE) up -d --wait db

db-down:
	$(COMPOSE) down

frontend:
	$(NPM) --prefix $(FRONTEND) run build

check:
	$(UV) run --locked python manage.py check --fail-level WARNING
	$(UV) run --locked python manage.py makemigrations --check --dry-run

test:
	mkdir -p build/reports
	$(UV) run --locked pytest --junitxml=build/reports/pytest.xml
	$(NPM) --prefix $(FRONTEND) test
	$(NPM) --prefix $(FRONTEND) run lint

lab05: db-up
	mkdir -p build/reports
	$(UV) run --locked pytest --cov=apps/ventas/pagos --cov-branch --cov-report=term-missing --cov-report=xml:build/reports/coverage-lab05.xml --junitxml=build/reports/pytest-lab05-full.xml

build: install frontend
	$(UV) run --locked python -m compileall -q apps config manage.py

package:
	$(UV) run --locked python scripts/package_practica3.py

verify: build check test package
	@echo 'BUILD SUCCESS: construccion, verificaciones, pruebas y ZIP completos.'

demo:
	$(UV) run --locked python manage.py migrate
	$(UV) run --locked python manage.py sembrar_demo

run:
	$(UV) run --locked python manage.py runserver

clean:
	rm -rf build dist frontend/inventario/dist
