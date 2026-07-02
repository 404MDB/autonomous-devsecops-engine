# Phase 5: OWASP ZAP Dynamic Application Security Testing (DAST)

## Objective

Integrate OWASP ZAP into the Jenkins DevSecOps pipeline to perform automated Dynamic Application Security Testing against the Dockerized Node.js dummy UPI gateway application.

The purpose of this phase is to test the application at runtime and identify web security issues such as missing security headers, insecure browser security policies, information disclosure, and other common web application misconfigurations.

---

## Tool Used

OWASP ZAP Baseline Scan

OWASP ZAP is executed as an ephemeral Docker container inside the Jenkins pipeline. The target application is also deployed temporarily as a Docker container during the scan.

This approach keeps the scanning environment isolated, repeatable, and automatically cleaned after each pipeline execution.

---

## Prerequisites

The following phases must be completed before this phase:

* Jenkins CI/CD pipeline configured
* Docker Outside of Docker architecture working
* Dummy UPI application Docker image successfully built
* TruffleHog secrets scanning integrated
* SonarQube SAST integrated
* Trivy container scanning integrated
* Jenkins able to run Docker commands inside the pipeline

---

## Step-by-Step Configuration

## Step 1: Temporary Docker Network Creation

A temporary Docker network is created so that the application container and the OWASP ZAP scanner container can communicate with each other.

```bash
docker network create devsecops-net || true
```

Network name:

```text
devsecops-net
```

This network exists only during the DAST stage and is removed during cleanup.

---

## Step 2: Temporary ZAP Report Volume Creation

A temporary Docker volume is created for ZAP report generation.

```bash
docker volume create zap-reports || true
```

Volume name:

```text
zap-reports
```

This volume is mounted to the ZAP working directory:

```text
/zap/wrk
```

---

## Step 3: Temporary Application Deployment

The hardened application image is started as a temporary container inside the DAST network.

```bash
docker run -d --name dummy-app --network devsecops-net dummy-upi-app:latest
```

Container name:

```text
dummy-app
```

Target URL used by OWASP ZAP:

```text
http://dummy-app:3000
```

Because both containers run on the same Docker network, ZAP can access the application using the container name.

---

## Step 4: OWASP ZAP Baseline Scan Execution

OWASP ZAP is executed as a Docker container.

```bash
docker run --name zap-scanner -u root --network devsecops-net -v zap-reports:/zap/wrk ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://dummy-app:3000 -r zap-report.html -I || true
```

Scanner container name:

```text
zap-scanner
```

Report generated:

```text
zap-report.html
```

The `-I` option allows the baseline scan to complete without failing the pipeline on warnings.

The `|| true` safeguard ensures that the pipeline continues even when ZAP reports warnings, so that the report can still be archived for academic review and evidence.

---

## Step 5: Copy ZAP Report to Jenkins Workspace

After the scan completes, the generated HTML report is copied from the ZAP container into the Jenkins workspace.

```bash
docker cp zap-scanner:/zap/wrk/zap-report.html ./zap-report.html
```

This makes the report available for Jenkins artifact archival.

---

## Step 6: Cleanup of Temporary Resources

The DAST environment is cleaned automatically after the scan.

```bash
docker stop dummy-app || true
docker rm dummy-app || true
docker rm zap-scanner || true
docker network rm devsecops-net || true
docker volume rm zap-reports || true
```

Resources removed:

* `dummy-app` container
* `zap-scanner` container
* `devsecops-net` Docker network
* `zap-reports` Docker volume

This prevents unused containers, networks, and volumes from remaining on the system after pipeline execution.

---

## Step 7: Jenkins Artifact Archival

The generated ZAP HTML report is archived as a Jenkins build artifact.

```groovy
archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true
```

This allows the report to be downloaded and reviewed from the Jenkins build page.

---

## Jenkins Pipeline Stage

```groovy
stage('DAST: OWASP ZAP Dynamic Scan') {
    steps {
        echo 'Spinning up application for dynamic security testing...'
        sh '''
            # 1. Create a temporary network and a dummy volume for ZAP
            docker network create devsecops-net || true
            docker volume create zap-reports || true

            # 2. Run the hardened application in the background
            docker run -d --name dummy-app --network devsecops-net dummy-upi-app:latest

            sleep 5
        '''

        echo 'Unleashing OWASP ZAP to attack the running application...'
        sh '''
            # 3. Run ZAP using the dummy volume to satisfy the internal check
            docker run --name zap-scanner -u root --network devsecops-net -v zap-reports:/zap/wrk ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://dummy-app:3000 -r zap-report.html -I || true

            # 4. Copy the report from the ZAP container into Jenkins workspace
            docker cp zap-scanner:/zap/wrk/zap-report.html ./zap-report.html
        '''
    }

    post {
        always {
            echo 'Tearing down test environment and saving ZAP report...'
            sh '''
                # 5. Stop and remove the test containers, networks, and volumes
                docker stop dummy-app || true
                docker rm dummy-app || true
                docker rm zap-scanner || true
                docker network rm devsecops-net || true
                docker volume rm zap-reports || true
            '''

            // 6. Save the HTML report as a Jenkins build artifact
            archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true
        }
    }
}
```

---

## Verified Jenkins Build Result

The Jenkins build successfully executed the OWASP ZAP DAST stage.

Final pipeline result:

```text
Finished: SUCCESS
```

ZAP scan summary:

```text
FAIL-NEW: 0
FAIL-INPROG: 0
WARN-NEW: 4
WARN-INPROG: 0
INFO: 0
IGNORE: 0
PASS: 63
```

This confirms that no new failing ZAP alerts were detected during the baseline scan.

---

## Warnings Detected

OWASP ZAP reported 4 warnings:

1. Storable and Cacheable Content
2. CSP: Failure to Define Directive with No Fallback
3. Permissions Policy Header Not Set
4. Cross-Origin-Embedder-Policy Header Missing or Invalid

These warnings are currently treated as non-blocking findings.

They are useful for future application hardening and can be remediated by improving HTTP response headers in the Node.js Express application.

---

## Security Value Added

This phase adds runtime security testing to the DevSecOps pipeline.

Benefits:

* Tests the application while it is running.
* Detects web application security misconfigurations.
* Generates a security report automatically.
* Archives evidence inside Jenkins.
* Runs in an isolated temporary Docker environment.
* Cleans up all temporary resources after execution.
* Adds DAST coverage to the Secure Software Development Lifecycle.

---

## Current Status

Phase 5 — OWASP ZAP DAST Integration: COMPLETE

The OWASP ZAP DAST stage is implemented, verified, and successfully executed in Jenkins.

Current result:

```text
ZAP FAIL-NEW: 0
ZAP WARN-NEW: 4
ZAP PASS: 63
Pipeline Status: SUCCESS
```
