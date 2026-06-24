pipeline {
    agent any

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
    }
}