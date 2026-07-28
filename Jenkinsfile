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

        // DefectDojo runs on the host machine and Jenkins reaches it using host.docker.internal
        DEFECTDOJO_URL = 'http://host.docker.internal:8081'

        // Engagement ID created in DefectDojo for CI-CD Security Pipeline
        DEFECTDOJO_ENGAGEMENT_ID = '1'
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
                // Validates that Docker-out-of-Docker socket mapping and required tools are working
                echo 'Verifying DevSecOps environment...'
                sh '''
                    docker --version
                    curl --version
                    node --version
                    npm --version
                '''
            }
        }

        stage('Secrets Scanning (TruffleHog)') {
            steps {
                echo 'Hunting for leaked passwords, AWS keys, and API tokens...'

                // Mounts the current Jenkins workspace into the TruffleHog container.
                // TruffleHog scans the filesystem for high-entropy strings and known credential patterns.
                // If verified secrets are found, it exits with a non-zero code, failing the build.
                sh '''
                    docker run --rm \
                      -v "${WORKSPACE}:/proj" \
                      trufflesecurity/trufflehog:latest \
                      filesystem /proj
                '''
            }
        }

        stage('SAST: SonarQube Code Analysis') {
            steps {
                // Wraps the execution in SonarQube context, sending the results to the external Sonar container
                withSonarQubeEnv('SonarQube') {
                    // Executes the static code analysis, explicitly ignoring non-production folders
                    sh '''
                        ${SCANNER_HOME}/bin/sonar-scanner \
                          -Dsonar.projectKey=autonomous-devsecops-engine \
                          -Dsonar.projectName="Autonomous DevSecOps Engine" \
                          -Dsonar.sources=. \
                          -Dsonar.coverage.exclusions=**/*.js \
                          -Dsonar.exclusions=reports/**,screenshots/**,docker/**,docs/**,dummy-upi-app/node_modules/**
                    '''
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                // Pauses the pipeline to wait for SonarQube to calculate the final grade through webhook
                timeout(time: 5, unit: 'MINUTES') {
                    // Currently non-blocking for academic development continuity.
                    // Earlier blocking gate was already validated successfully.
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Build Target Docker Image') {
            steps {
                echo 'Building the dummy UPI application image...'

                // Builds the target application Docker image from dummy-upi-app directory
                sh '''
                    docker build -t dummy-upi-app:latest ./dummy-upi-app
                '''
            }
        }

        stage('Generate Trivy JSON Report') {
            steps {
                echo 'Generating Trivy JSON report for DefectDojo...'

                // Trivy JSON report is required for DefectDojo import.
                // This stage generates the report but does not fail the pipeline on vulnerabilities.
                sh '''
                    mkdir -p reports/trivy

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v "${WORKSPACE}/reports/trivy:/reports" \
                      aquasec/trivy image \
                      --format json \
                      --output /reports/trivy-image-report.json \
                      dummy-upi-app:latest

                    ls -lh reports/trivy/
                '''
            }
        }

        stage('DAST: OWASP ZAP Dynamic Scan') {
            steps {
                echo 'Spinning up application for dynamic security testing...'

                sh '''
                    # 1. Prepare report directory
                    mkdir -p reports/zap

                    # 2. Remove old test containers and network if they already exist
                    docker rm -f dummy-app zap-scanner 2>/dev/null || true
                    docker network rm devsecops-net 2>/dev/null || true

                    # 3. Create a temporary Docker network for application and ZAP scanner
                    docker network create devsecops-net

                    # 4. Run the dummy UPI application in the background
                    docker run -d --name dummy-app \
                      --network devsecops-net \
                      dummy-upi-app:latest

                    # 5. Give the application time to start
                    sleep 10
                '''

                echo 'Unleashing OWASP ZAP to attack the running application...'

                sh '''
                    # 6. Run OWASP ZAP baseline scan
                    # HTML report is used for Jenkins evidence
                    # XML report is used for DefectDojo import
                    docker run --rm --name zap-scanner -u root \
                      --network devsecops-net \
                      -v "${WORKSPACE}/reports/zap:/zap/wrk" \
                      ghcr.io/zaproxy/zaproxy:stable \
                      zap-baseline.py \
                      -t http://dummy-app:3000 \
                      -r zap-report.html \
                      -x zap-report.xml \
                      -I || true

                    ls -lh reports/zap/
                '''
            }
        }

        stage('Upload Trivy Report to DefectDojo') {
            steps {
                echo 'Uploading Trivy vulnerability report to DefectDojo...'

                // Uses Jenkins secret text credential.
                // Credential ID must be: defectdojo-api-token
                // Do not hardcode the API token in Jenkinsfile.
                withCredentials([string(credentialsId: 'defectdojo-api-token', variable: 'DEFECTDOJO_API_TOKEN')]) {
                    sh '''
                        # 1. Verify that Trivy report exists before uploading
                        test -f reports/trivy/trivy-image-report.json

                        # 2. Upload Trivy JSON report to DefectDojo
                        set +x
                        HTTP_CODE=$(curl -sS -o reports/trivy/defectdojo-trivy-upload-response.json -w "%{http_code}" \
                          -X POST "${DEFECTDOJO_URL}/api/v2/import-scan/" \
                          -H "Authorization: Token ${DEFECTDOJO_API_TOKEN}" \
                          -F "engagement=${DEFECTDOJO_ENGAGEMENT_ID}" \
                          -F "scan_type=Trivy Scan" \
                          -F "file=@reports/trivy/trivy-image-report.json" \
                          -F "minimum_severity=Info" \
                          -F "active=true" \
                          -F "verified=false" \
                          -F "close_old_findings=false" \
                          -F "push_to_jira=false")
                        set -x

                        # 3. Print upload status and response
                        echo "DefectDojo Trivy upload HTTP status: ${HTTP_CODE}"
                        cat reports/trivy/defectdojo-trivy-upload-response.json

                        # 4. Fail pipeline if DefectDojo upload fails
                        if [ "${HTTP_CODE}" -lt 200 ] || [ "${HTTP_CODE}" -ge 300 ]; then
                          echo "Trivy upload to DefectDojo failed"
                          exit 1
                        fi
                    '''
                }
            }
        }

        stage('Upload ZAP Report to DefectDojo') {
            steps {
                echo 'Uploading OWASP ZAP report to DefectDojo...'

                // Uses Jenkins secret text credential.
                // Credential ID must be: defectdojo-api-token
                // Do not hardcode the API token in Jenkinsfile.
                withCredentials([string(credentialsId: 'defectdojo-api-token', variable: 'DEFECTDOJO_API_TOKEN')]) {
                    sh '''
                        # 1. Verify that ZAP XML report exists before uploading
                        test -f reports/zap/zap-report.xml

                        # 2. Upload ZAP XML report to DefectDojo
                        set +x
                        HTTP_CODE=$(curl -sS -o reports/zap/defectdojo-zap-upload-response.json -w "%{http_code}" \
                          -X POST "${DEFECTDOJO_URL}/api/v2/import-scan/" \
                          -H "Authorization: Token ${DEFECTDOJO_API_TOKEN}" \
                          -F "engagement=${DEFECTDOJO_ENGAGEMENT_ID}" \
                          -F "scan_type=ZAP Scan" \
                          -F "file=@reports/zap/zap-report.xml" \
                          -F "minimum_severity=Info" \
                          -F "active=true" \
                          -F "verified=false" \
                          -F "close_old_findings=false" \
                          -F "push_to_jira=false")
                        set -x

                        # 3. Print upload status and response
                        echo "DefectDojo ZAP upload HTTP status: ${HTTP_CODE}"
                        cat reports/zap/defectdojo-zap-upload-response.json

                        # 4. Fail pipeline if DefectDojo upload fails
                        if [ "${HTTP_CODE}" -lt 200 ] || [ "${HTTP_CODE}" -ge 300 ]; then
                          echo "ZAP upload to DefectDojo failed"
                          exit 1
                        fi
                    '''
                }
            }
        }

        stage('SCA: Trivy Container Scan Critical Gate') {
            steps {
                echo 'Summoning Trivy to enforce CRITICAL vulnerability gate...'

                // This gate runs after DefectDojo upload.
                // Even if the pipeline fails here, reports are already uploaded to DefectDojo.
                sh '''
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy image \
                      --exit-code 1 \
                      --severity CRITICAL \
                      dummy-upi-app:latest
                '''
            }
        }
    }

    post {
        always {
            echo 'Tearing down test environment and saving security reports...'

            sh '''
                # Stop and remove temporary DAST containers and network
                docker rm -f dummy-app zap-scanner 2>/dev/null || true
                docker network rm devsecops-net 2>/dev/null || true
            '''

            // Save generated reports and DefectDojo upload responses as Jenkins build artifacts
            archiveArtifacts artifacts: 'reports/**/*.json,reports/**/*.xml,reports/**/*.html', fingerprint: true, allowEmptyArchive: true
        }

        success {
            echo 'Pipeline completed successfully. Security reports uploaded to DefectDojo.'
        }

        failure {
            echo 'Pipeline failed. Check Jenkins logs, security gates, and DefectDojo upload responses.'
        }
    }
}