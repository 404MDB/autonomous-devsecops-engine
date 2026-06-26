pipeline {
    agent any

    // This block summons Node.js so SonarQube can scan JavaScript
    tools {
        nodejs 'NodeJS' 
    }

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
                withSonarQubeEnv('SonarQube') { 
                    sh """
                    \${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=autonomous-devsecops-engine \
                      -Dsonar.projectName="Autonomous DevSecOps Engine" \
                      -Dsonar.sources=. \
                      -Dsonar.exclusions=reports/**,screenshots/**,docker/**,docs/**
                    """
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                // Jenkins will pause here and wait for SonarQube's webhook response
                timeout(time: 5, unit: 'MINUTES') {
                    // If the gate fails, 'abortPipeline: true' instantly kills the build
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Target Docker Image') {
            steps {
                echo 'Building the vulnerable UPI application image...'
                dir('dummy-upi-app') {
                    sh 'docker build -t dummy-upi-app:latest .'
                }
            }
        }

        stage('SCA: Trivy Container Scan') {
            steps {
                echo 'Summoning Trivy to scan the application image...'
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image dummy-upi-app:latest'
            }
        }
    }
}