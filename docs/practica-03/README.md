# Práctica 03 — Construcción automática

Este directorio reúne los tres entregables de la práctica. El modelo principal
es el [`Makefile`](../../Makefile); los scripts Python son auxiliares invocados
por ese modelo y no una configuración paralela.

## Entregable 1. Proyecto GitHub

- Rama de trabajo: `doc/automatic`.
- Commit base de `dev`: `63e48ac75026d682c231efb724f436e265489653`.
- Commits de implementación:
  - `7617d60` — versión de Node y compatibilidad del frontend.
  - `92e73c1` — contrato del artefacto ZIP.
  - `5fca1ce` — settings de construcción y `STATIC_ROOT`.
  - `5766030` — empaquetado, verificación y pruebas.
  - `41e2d94` — orquestación con GNU Make.
  - `9ecb152` — tutorial, índice y evidencias de ejecución.
  - `2148eb2` — invalidación preventiva de artefactos anteriores.
  - `d6538e6` — verificación de los recursos CSS del frontend.
- La rama no se publica automáticamente. Véase [evidencias](evidencias.md).

## Entregable 2. Modelo de construcción

El comando principal, ejecutado desde la raíz, es:

```bash
make build
```

| Requisito | Archivo, campo o etapa real | Evidencia |
| --- | --- | --- |
| Nombre y versión | `pyproject.toml`, `[project]` | `software-textil-0.1.0.zip` y manifiesto interno. |
| Tipo de archivo | `[tool.software-textil.release] format = "zip"` | ZIP y `.zip.sha256` en `dist/`. |
| Herramientas y versiones | `.python-version`, `.node-version`, `package.json#engines`, `prerequisites` | Versiones efectivas en [evidencias](evidencias.md). |
| Opciones de construcción | `vite.config.js`, objetivos `frontend`, `check` y `static` | Base `/static/zuren/`, nombres estables y salida `dist/`. |
| Dependencias | `uv.lock` y `package-lock.json` | `uv sync --locked` y `npm ci`. |
| Pruebas | Objetivos `frontend-check`, `check` y `test` | Resultados y bloqueos reales en [evidencias](evidencias.md). |
| Empaquetado | `scripts/package_release.py`, objetivo `package` | Manifiesto, 380 entradas observadas y checksum. |
| Verificación | `scripts/verify_release.py`, objetivo `verify-release` | Extracción temporal y entorno Python independiente. |

## Entregable 3. Tutorial

El procedimiento reproducible está en [tutorial.md](tutorial.md). Los comandos
ejecutados, resultados observados y verificaciones pendientes se separan en
[evidencias.md](evidencias.md).
