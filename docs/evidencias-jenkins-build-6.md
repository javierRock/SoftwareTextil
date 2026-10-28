# Evidencia Jenkins - build local 6

Jenkins ejecutado localmente con Jenkins 2.568.3 y Java 21.0.12.1.

- Job: `SoftwareTextil-CI`
- Build: `6`
- Resultado: **SUCCESS**
- Duración: 22.856 segundos
- URL local durante la ejecución: http://127.0.0.1:18080/job/SoftwareTextil-CI/6/
- Console Output: `evidencias-jenkins-console-build-6.txt`
- Artefactos Jenkins: ZIP, checksum, frontend compilado y reportes JUnit/aplicación

## Pipeline Overview

| Etapa | Estado |
| --- | --- |
| Git Checkout | PASS |
| Tool Check | PASS |
| Database | PASS |
| Build | PASS |
| Test and Quality | PASS |
| SonarQube Analysis (optional) | OMITIDA: RUN_SONAR=false |
| Package and Publish | PASS |
| Run Published Application | PASS |
| Post Actions | PASS |

El Console Output registra:

- checkout de la revisión `14ecec5`;
- Java, Git, Make, uv, Node, npm y Docker disponibles;
- PostgreSQL 16 saludable;
- Vite transformando 55 módulos;
- Django sin incidencias;
- 271 pruebas Python aprobadas;
- 4 pruebas JavaScript aprobadas;
- ESLint correcto;
- ZIP y SHA-256 generados;
- datos demo cargados;
- aplicación Django comprobada mediante HTTP en el puerto 8083;
- limpieza de proceso y base de datos;
- `JENKINS BUILD SUCCESS: CI completed.`

SonarQube aparece como etapa opcional omitida porque no se configuró un servidor ni un token. Esta decisión es explícita y segura: no se incluyeron credenciales en el repositorio.

