pipeline {
    agent any
    options {
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
    }
    parameters {
        booleanParam(name: 'RUN_SONAR', defaultValue: true,
            description: 'Ejecutar el análisis y esperar el Quality Gate. Desactivar solo para validar la configuración de Jenkins.')
        string(name: 'SONAR_PROJECT_KEY', defaultValue: 'softwaretextil-dev-ci',
            description: 'Clave de CI para dev. Usar una clave separada para una comparación.')
    }
    environment {
        DB_NAME = 'software_textil_quality_jenkins'
        DB_HOST = '127.0.0.1'
        SONAR_HOST_URL = 'http://localhost:9000'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'make clean'
            }
        }
        stage('Construcción') {
            steps {
                sh 'make deps frontend-build'
            }
        }
        stage('PostgreSQL de pruebas') {
            steps {
                script {
                    // El puerto asignado por Docker permite probar varios jobs en el mismo agente.
                    env.COMPOSE_PROJECT_NAME = sh(returnStdout: true, script: '''
                        printf 'textil-%s' "$BUILD_TAG" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9_-' '-'
                    ''').trim()
                    env.DB_PORT = sh(returnStdout: true, script: '''
                        set -eu
                        export DB_PORT=0
                        docker compose -f compose.quality.yml up -d --wait db >&2
                        endpoint=$(docker compose -f compose.quality.yml port db 5432)
                        port=${endpoint##*:}
                        test "$port" -gt 0
                        printf '%s\n' "$port"
                    ''').trim()
                }
            }
        }
        stage('Pruebas automatizadas') {
            steps {
                sh 'make django-check reportes frontend-reportes'
                sh 'npm --prefix frontend/inventario run lint'
            }
            post {
                always {
                    junit testResults: 'build/reports/*junit.xml', allowEmptyResults: true
                }
            }
        }
        stage('Distribución verificable') {
            steps {
                sh 'make collect-static release-zip release-verify'
                archiveArtifacts artifacts: 'dist/*.zip,dist/*.zip.sha256', fingerprint: true
            }
        }
        stage('SonarQube y Quality Gate') {
            when { expression { params.RUN_SONAR } }
            steps {
                withCredentials([string(credentialsId: 'sonarqube-softwaretextil', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        set +x
                        set -eu
                        test -s build/reports/coverage.xml
                        test -s build/reports/frontend-lcov.info
                        sonar-scanner \
                          -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                          -Dsonar.projectName="$SONAR_PROJECT_KEY" \
                          -Dsonar.python.coverage.reportPaths=build/reports/coverage.xml \
                          -Dsonar.qualitygate.wait=true \
                          -Dsonar.qualitygate.timeout=300
                    '''
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'build/reports/**', allowEmptyArchive: true
        }
        cleanup {
            sh '''
                if [ -n "${COMPOSE_PROJECT_NAME:-}" ]; then
                    docker compose -f compose.quality.yml down --volumes
                fi
            '''
        }
    }
}
