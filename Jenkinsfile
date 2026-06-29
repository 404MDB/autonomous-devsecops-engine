pipeline {
    // Defines where the pipeline runs. 'any' means it will run on the available Jenkins node.
    agent any

    // Automatically installs and injects necessary build tools into the pipeline environment.
    tools {
        // Required for SonarQube's JavaScript/TypeScript analysis engine
        nodejs 'NodeJS' 
    }

    environment {
        // Maps the SonarScanner tool installed in Jenkins to an environment variable
        SCANNER_HOME = tool 'SonarScanner'
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Pulls the latest code from the GitHub repository linked to this Jenkins job
                checkout scm
                echo 'Code checked out securely from GitHub!'
            }
        }

        stage('DevSecOps Environment Check') {
            steps {
                // Validates that Docker-out-of-Docker (DooD) socket mapping is working
                echo 'Verifying Docker-out-of-Docker connectivity...'
                sh 'docker --version'
            }
        }

        stage('Secrets Scanning (TruffleHog)') {
            steps {
                echo 'Hunting for leaked passwords, AWS keys, and API tokens...'
                // Mounts the current Jenkins workspace into the TruffleHog container.
                // TruffleHog scans the filesystem for high-entropy strings and known credential patterns.
                // If verified secrets are found, it exits with a non-zero code, failing the build.
                sh 'docker run --rm -v ${WORKSPACE}:/proj trufflesecurity/trufflehog:latest filesystem /proj'
            }
        }

        stage('SAST: SonarQube Code Analysis') {
            steps {
                // Wraps the execution in SonarQube context, sending the results to the external Sonar container
                withSonarQubeEnv('SonarQube') { 
                    // Executes the static code analysis, explicitly ignoring non-production folders
                    sh """
                    \${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=autonomous-devsecops-engine \
                      -Dsonar.projectName="Autonomous DevSecOps Engine" \
                      -Dsonar.sources=. \
                      -Dsonar.coverage.exclusions=**/*.js \
                      -Dsonar.exclusions=reports/**,screenshots/**,docker/**,docs/**
                    """
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                // Pauses the pipeline to wait for SonarQube to calculate the final grade (via Webhook)
                timeout(time: 5, unit: 'MINUTES') {
                    // 'abortPipeline: true' makes Jenkins act as a security bouncer. 
                    // If SonarQube reports a failure (e.g., Critical Vulnerabilities), the build dies here.
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Target Docker Image') {
            steps {
                echo 'Building the vulnerable UPI application image...'
                // Navigates into the application folder to build the Docker image
                dir('dummy-upi-app') {
                    sh 'docker build -t dummy-upi-app:latest .'
                }
            }
        }

        stage('SCA: Trivy Container Scan') {
            steps {
                echo 'Summoning Trivy to scan the application image...'
                // Mounts the Docker socket to allow Trivy to scan the image we just built.
                // It looks for CVEs in the base OS layer (Alpine) and package.json dependencies.
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 1 --severity CRITICAL dummy-upi-app:latest'
            }
        }

        stage('DAST: OWASP ZAP Dynamic Scan') {
            steps {
                echo 'Spinning up application for dynamic security testing...'
                sh '''
                    # 1. Create a temporary network so ZAP and the App can communicate
                    docker network create devsecops-net || true

                    # 2. Run the hardened application in the background
                    docker run -d --name dummy-app --network devsecops-net dummy-upi-app:latest

                    # Give the Node.js server 5 seconds to boot up
                    sleep 5
                '''
                
                echo 'Unleashing OWASP ZAP to attack the running application...'
                sh '''
                    # 3. Run ZAP Baseline Scan against the running container
                    # We removed --rm and the -v volume mount so the container sticks around temporarily.
                    docker run --name zap-scanner -u root --network devsecops-net ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://dummy-app:3000 -r zap-report.html -I || true
                    
                    # 4. Reach into the stopped ZAP container and copy the report into Jenkins' workspace!
                    docker cp zap-scanner:/zap/wrk/zap-report.html ./zap-report.html
                '''
            }
            post {
                always {
                    echo 'Tearing down test environment and saving ZAP report...'
                    sh '''
                        # 5. Stop and remove the test container and network
                        docker stop dummy-app || true
                        docker rm dummy-app || true
                        docker rm zap-scanner || true   # Clean up the ZAP container now that we have the file!
                        docker network rm devsecops-net || true
                    '''
                    // 6. Save the HTML report as a Jenkins build artifact
                    archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true
                }
            }
        }
    }
}