// Pipeline declarativo de integración continua para SoftwareTextil.
// SoftwareTextil usa Django/React/PostgreSQL, por eso Make coordina el build.
pipeline {
    agent any
    options {
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    parameters {
        booleanParam(name: 'RUN_SONAR', defaultValue: false,
            description: 'Ejecutar SonarQube si ya fue configurado en Jenkins.')
    }
    environment {
        DB_NAME = 'software_textil_quality_jenkins'
        DB_USER = 'postgres'
        DB_PASSWORD = 'postgres'
        DB_HOST = '127.0.0.1'
        DB_PORT = '55432'
        DJANGO_SETTINGS_MODULE = 'config.settings.dev'
        COMPOSE_PROJECT = 'softwaretextil-jenkins'
    }
    stages {
        stage('Git Checkout') {
            steps { checkout scm }
        }
        stage('Tool Check') {
            steps {
                sh '''
                    set -eux
                    java -version
                    git --version
                    make --version | head -n 1
                    uv --version
                    node --version
                    npm --version
                    docker compose version
                '''
            }
        }
        stage('Database') {
            steps { sh 'make db-up' }
        }
        stage('Build') {
            steps { sh 'make build' }
        }
        stage('Test and Quality') {
            steps {
                sh 'make check'
                sh 'make test'
                sh 'make quality'
            }
            post {
                always {
                    junit testResults: 'build/reports/pytest.xml,build/reports/pytest-quality-full.xml', allowEmptyResults: true
                }
            }
        }
        stage('SonarQube Analysis (optional)') {
            when { expression { params.RUN_SONAR } }
            steps {
                withSonarQubeEnv('sonarqube-local') {
                    sh '''
                        set -eux
                        sonar-scanner \
                          -Dsonar.projectKey=software-textil \
                          -Dsonar.projectName=software-textil \
                          -Dsonar.sources=apps,config,frontend/inventario/src \
                          -Dsonar.exclusions='**/migrations/**,frontend/inventario/node_modules/**'
                    '''
                }
            }
        }
        stage('Package and Publish') {
            steps {
                sh 'make package'
                archiveArtifacts artifacts: 'dist/*,frontend/inventario/dist/**', fingerprint: true
            }
        }
        stage('Run Published Application') {
            steps {
                sh '''
                    set -eux
                    make demo
                    mkdir -p build/reports
                    nohup uv run --locked python manage.py runserver 0.0.0.0:8083 \
                      > build/reports/application.log 2>&1 &
                    echo $! > build/application.pid
                    sleep 5
                    curl --fail --silent http://127.0.0.1:8083/ > build/reports/application.html
                '''
            }
            post {
                always { archiveArtifacts artifacts: 'build/reports/application.*', allowEmptyArchive: true }
            }
        }
    }
    post {
        always {
            sh '''
                if [ -f build/application.pid ]; then
                    kill "$(cat build/application.pid)" || true
                fi
                make db-down || true
            '''
            archiveArtifacts artifacts: 'build/reports/**', allowEmptyArchive: true
        }
        success { echo 'JENKINS BUILD SUCCESS: CI completed.' }
        failure { echo 'JENKINS BUILD FAILURE: revisar la etapa roja y Console Output.' }
    }
}
