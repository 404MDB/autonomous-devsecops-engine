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

        stage('Build Target Docker Image') {
            steps {
                echo 'Building the vulnerable UPI application image...'
                // The dir() command tells Jenkins to go into your new folder
                dir('dummy-upi-app') {
                    sh 'docker build -t dummy-upi-app:latest .'
                }
            }
        }

        stage('SCA: Trivy Container Scan') {
            steps {
                echo 'Summoning Trivy to scan the application image...'
                // Jenkins uses the Docker socket to spin up Trivy and scan the image we just built
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image dummy-upi-app:latest'
            }
        }
    }
}