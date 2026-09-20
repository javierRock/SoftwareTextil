# Evidencias de ejecución — Práctica 03

Fecha: 16-09-2026. Rama: `doc/automatic`. Base:
`63e48ac75026d682c231efb724f436e265489653`.

## Comandos ejecutados y resultados observados

| Comando | Resultado observado |
| --- | --- |
| `make prerequisites` | Make 4.4.1, uv 0.9.10, Python 3.11.15, Node 26.7.0 y npm 12.0.2. |
| `npm test` | 4 pruebas aprobadas, 0 fallos. |
| `npm run lint` | Aprobado. |
| `npm run build` | Vite 7.3.6; generó `index.html`, `assets/app.css` y `assets/app.js`. |
| Ruff sobre `scripts`, `tests/release` y `config/settings/build.py` | Aprobado. |
| `pytest tests/release/test_release.py -q` | 10 pruebas aprobadas. |
| `manage.py check` con settings de build | 0 incidencias. |
| `makemigrations --check --dry-run` | No detectó cambios; avisó que `software_textil` no existía. |
| `collectstatic --noinput --clear` | 159 archivos copiados a `build/staticfiles`. |
| `python -m scripts.package_release` | Generó ZIP y `.sha256`. |
| `python -m scripts.verify_release` | Checksum, contenido, extracción, `uv sync --no-dev` y check Django independientes aprobados. |
| `sha256sum -c` desde `dist/` | `software-textil-0.1.0.zip: OK`. |
| Inspección programática del ZIP | 380 entradas, 379 en inventario, SPA/estáticos presentes y exclusiones ausentes. |

El manifiesto observado registró correctamente `source_state = "con cambios"`;
no atribuyó el contenido modificado a un checkout limpio.

## Construcción completa

Se ejecutó desde cero:

```bash
make clean
make build
```

Dependencias, pruebas frontend, lint frontend y Vite finalizaron. El proceso se
detuvo en `uv run --locked ruff check .` con 58 errores preexistentes, sobre
todo líneas largas en `apps/inventario/application/reportes.py` y sus pruebas,
además de firmas extensas en catálogo. Make conservó el código de salida y no
anunció éxito ni produjo un ZIP como resultado de esa ejecución fallida.

No se silenciaron reglas, no se redujeron umbrales y no se modificaron esos
módulos ajenos. El empaquetado se verificó después mediante sus comandos
directos para validar el entregable técnico sin presentar `make build` como
aprobado.

## Verificaciones pendientes o bloqueadas

| Verificación | Estado y motivo |
| --- | --- |
| `docker compose up -d --wait db` | No ejecutada: el cliente no pudo conectar con `/var/run/docker.sock`; daemon inactivo. |
| Suite Python completa contra PostgreSQL | No ejecutada: `make build` se detuvo antes en Ruff y la base `software_textil` no existía. |
| Prueba manual del servidor con PostgreSQL | No ejecutada por el mismo bloqueo del daemon/base. |
| Build completo verde | Pendiente de corregir los 58 errores Ruff preexistentes fuera del alcance. |
| Publicación de `doc/automatic` | Pendiente; no se hizo push porque no fue autorizado. |

También se observó que `npm ci` reportó cinco vulnerabilidades de severidad alta
y un aviso de script de instalación bloqueado para `esbuild@0.28.1`; pese al
aviso, las pruebas, ESLint y el build Vite finalizaron correctamente. No se
ejecutó `npm audit fix` porque actualizar dependencias sin revisión excede el
alcance.

## Publicación pendiente

Después de revisar los commits locales, el responsable puede publicar la rama:

```bash
git push -u origin doc/automatic
```

No se realizó merge, force-push ni release pública.
