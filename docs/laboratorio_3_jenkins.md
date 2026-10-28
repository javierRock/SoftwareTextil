# Laboratorio 03: Integración continua con Jenkins

## Adaptación al repositorio

El PDF propone como ejemplo un proyecto Java con Maven y SonarQube. SoftwareTextil es un proyecto diferente: usa Django/Python, React/Vite y PostgreSQL. Por eso se conservan las etapas del laboratorio, pero se ejecutan con las herramientas reales del repositorio.

| Etapa del laboratorio | Implementación |
| --- | --- |
| Pipeline de prueba | Pipeline declarativo en `Jenkinsfile` |
| Pipeline Git | `stage('Git Checkout')` con `checkout scm` |
| Build | `make build` |
| Pruebas | `make check` y `make test` |
| SonarQube | Etapa opcional `RUN_SONAR`, desactivada por defecto |
| Publicación | ZIP como artefacto Jenkins y aplicación Django en puerto 8083 |

No se debe afirmar que Maven compiló SoftwareTextil: no es un proyecto Maven. Tampoco se debe copiar un token de SonarQube en el Jenkinsfile; los tokens son credenciales de Jenkins.

## 1. Requisitos

El agente que ejecuta Jenkins necesita Java 17+, Git, Docker Desktop con Compose, GNU Make, uv, Node.js 24 y npm. SonarQube y `sonar-scanner` son opcionales hasta configurar el análisis de calidad.

```bash
java -version
git --version
make --version
uv --version
node --version
npm --version
docker compose version
```

## 2. Instalar Jenkins

Descargar Jenkins LTS desde <https://www.jenkins.io/download/>. La forma indicada en el laboratorio es ejecutar el WAR:

```bash
java -jar jenkins.war --httpPort=8080
```

Abrir <http://localhost:8080>, copiar la contraseña inicial que aparece en la consola, cambiar la contraseña del administrador e instalar los plugins sugeridos.

En **Manage Jenkins > Plugins** confirmar o instalar Pipeline, Git, Pipeline: Stage View y JUnit. Instalar SonarQube Scanner for Jenkins solo si se ejecutará SonarQube.

En **Manage Jenkins > Tools** comprobar que Git, Java 17, Make, uv, Node/npm y Docker estén disponibles para el usuario del agente.

## 3. Crear el Pipeline

1. Seleccionar **New Item**.
2. Escribir `SoftwareTextil-CI`.
3. Seleccionar **Pipeline**.
4. En **Pipeline > Definition**, escoger **Pipeline script from SCM**.
5. Seleccionar **Git**, indicar la URL del repositorio y la rama `codex/practica-3-construccion-automatica` cuando esté publicada.
6. Usar `Jenkinsfile` como **Script Path**.
7. Guardar y pulsar **Build Now**.

Para una prueba sin GitHub se puede pegar el contenido del `Jenkinsfile` directamente en **Pipeline script**. Para una entrega reproducible conviene que Jenkins obtenga el archivo desde SCM.

## 4. Etapas visibles

El Pipeline contiene las siguientes etapas en **Pipeline Overview**:

1. `Git Checkout`: obtiene la revisión del job.
2. `Tool Check`: registra versiones de Java, Git, Make, uv, Node, npm y Docker.
3. `Database`: inicia PostgreSQL 16 con `make db-up`.
4. `Build`: instala dependencias y compila backend/frontend con `make build`.
5. `Test and Quality`: ejecuta Django, migraciones, 271 pruebas Python, 4 pruebas JavaScript y ESLint.
6. `SonarQube Analysis (optional)`: se ejecuta solo con el parámetro `RUN_SONAR=true`.
7. `Package and Publish`: crea el ZIP y lo archiva.
8. `Run Published Application`: carga datos demo, inicia Django en `8083` y comprueba HTTP.

El bloque `post` guarda reportes, detiene el proceso temporal y baja PostgreSQL aunque el build falle.

## 5. SonarQube opcional

Para activar la etapa del PDF:

1. Instalar el plugin **SonarQube Scanner for Jenkins**.
2. En **Manage Jenkins > System > SonarQube servers**, crear `sonarqube-local` con la URL del servidor.
3. En **Manage Jenkins > Tools**, configurar `sonar-scanner`.
4. Crear el proyecto `software-textil` y su token en SonarQube.
5. Guardar el token como credencial secreta de Jenkins.
6. Ejecutar el job con `RUN_SONAR=true`.

El token no se incluye en el repositorio ni en capturas. El ejemplo del PDF contiene un token escrito directamente, pero eso no es seguro.

## 6. Evidencias solicitadas por el PDF

- **Console Output:** abrir el número de build y guardar el texto o una captura. Deben verse checkout, etapas, pruebas, artefactos y el mensaje final.
- **Pipeline Overview:** capturar las etapas verdes. Si SonarQube no está configurado, explicar que la etapa opcional se dejó desactivada.
- **Artifacts:** verificar el ZIP, el checksum, el XML JUnit y los reportes de aplicación.
- **Aplicación publicada:** abrir `http://localhost:8083/` mientras el servidor esté ejecutándose.

Texto sugerido para la memoria:

> El Pipeline `SoftwareTextil-CI` obtuvo el código desde Git, levantó PostgreSQL, instaló dependencias desde los lockfiles, construyó Django/React, ejecutó las pruebas, empaquetó el proyecto y archivó el resultado. La construcción fue exitosa cuando todas las etapas finalizaron en verde.

## 7. Validación local antes de Jenkins

```bash
make db-up
make verify
make demo
make run
```

La ejecución local verificada produjo 271 pruebas Python aprobadas, 4 pruebas JavaScript aprobadas, ESLint correcto, Django sin incidencias, ninguna migración pendiente, ZIP con SHA-256 y respuestas HTTP 200 para la aplicación compilada.

## 8. Problemas frecuentes

| Problema | Solución |
| --- | --- |
| Docker no está disponible | Abrir Docker Desktop o usar un agente con acceso al daemon |
| `uv` no está en PATH | Instalarlo para el usuario del agente o configurarlo en Jenkins Tools |
| Puerto 55432 ocupado | Detener el proceso o modificar `DB_PORT` en el job |
| No aparece el Jenkinsfile | Revisar la rama, la URL SCM y `Script Path` |
| SonarQube falla | Ejecutar primero con `RUN_SONAR=false` y configurar servidor/scanner después |
| No hay XML JUnit | Revisar Console Output; `make test` crea `build/reports/pytest.xml` |
| Puerto 8083 ocupado | Detener la aplicación anterior o cambiar el puerto del Jenkinsfile |

## 9. Estado de publicación

La rama y los commits de la práctica están preparados localmente. La publicación en GitHub requiere autorizar el permiso `workflow`, porque el repositorio contiene configuración de automatización. Hasta que el push sea aceptado, no se debe presentar GitHub Actions como ejecutado.

El archivo ejecutable es `Jenkinsfile`; esta memoria explica la instalación, configuración, ejecución y evidencias del laboratorio.

## 10. Ejecución Jenkins local verificada

El job local `SoftwareTextil-CI` se ejecutó con Jenkins 2.568.3 y terminó con **SUCCESS** en el build 6. El resumen de etapas está en `docs/evidencias-jenkins-build-6.md` y el registro completo está en `docs/evidencias-jenkins-console-build-6.txt`.

La ejecución real confirmó checkout, herramientas, PostgreSQL, build, pruebas, empaquetado y comprobación HTTP de la aplicación. El artefacto ZIP, el checksum, el XML JUnit, el frontend compilado y los reportes quedaron archivados por Jenkins. SonarQube fue omitido explícitamente porque es una etapa opcional que requiere configurar un servidor y credenciales.
