pipeline {
    agent any

    environment {
        // Must match the exact name given in Jenkins Global Tool Configuration
        SCANNER_HOME = tool 'SonarScanner'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                echo 'Code checked out securely from GitHub!'
            }
        }

        stage('DevSecOps Environment Check') {
            steps {
                echo 'Verifying Docker-out-of-Docker connectivity...'
                sh 'docker --version'
                sh 'docker ps'
            }
        }

        stage('SAST: SonarQube Code Analysis') {
            steps {
                // Must match the exact Server Name in Jenkins System Configuration
                withSonarQubeEnv('SonarQube') { 
                    sh """
                    ${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=autonomous-devsecops-engine \
                      -Dsonar.projectName="Autonomous DevSecOps Engine" \
                      -Dsonar.sources=. \
                      -Dsonar.exclusions=reports/**,screenshots/**,docker/**,docs/**
                    """
                }
            }
        }
    }
}