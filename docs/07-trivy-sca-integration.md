# Phase 4: Software Composition Analysis (SCA) & Quality Gate Enforcement

## Objective
Implement container image scanning using Trivy (SCA) and enforce strict security policies by configuring Jenkins to automatically abort pipelines that fail SonarQube Quality Gates.

## Prerequisites
* Phase 3 completed (SonarQube SAST integration).
* Target application (Node.js dummy UPI gateway) with known vulnerabilities and outdated dependencies generated.

---

## Step-by-Step Configuration

### Step 1: Quality Gate Webhook Configuration
To allow SonarQube to actively communicate analysis results back to the CI/CD pipeline, a webhook was established.
* **Endpoint:** `http://172.17.0.1:8080/sonarqube-webhook/`
* This establishes a direct, asynchronous communication line from the SonarQube container back to the Jenkins controller across the Docker bridge network.

### Step 2: Jenkins NodeJS Runtime Injection
To prevent runtime parsing errors during JavaScript SAST analysis, the official NodeJS Jenkins Plugin was installed.
* **Tool Configuration:** Injected `NodeJS` directly into the declarative pipeline environment via the `tools {}` block, ensuring the SonarScanner could successfully execute the JavaScript analysis engine.

### Step 3: SCA Implementation with Trivy
Trivy was integrated to scan the resulting Docker image for OS-level and third-party dependency vulnerabilities (CVEs).
* Leveraged the existing Docker-out-of-Docker (DooD) socket to run the Trivy scanner dynamically as an ephemeral container (`docker run --rm ... aquasec/trivy`), eliminating the need to install Trivy binaries directly on the Jenkins server.

### Step 4: Pipeline Security Enforcement
The `Jenkinsfile` was updated to include a blocking `Quality Gate Check` stage immediately following the SAST scan.

```groovy
        stage('Quality Gate Check') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
```
**Verification & Outcomes**
SAST Execution: SonarScanner successfully analyzed the Node.js source code, identifying critical Security Hotspots (hardcoded cryptography keys, unparameterized SQL queries) and 0% unit test coverage.

Quality Gate Trip: SonarQube correctly evaluated the code against the baseline policy and flagged the project as Failed.

Pipeline Abort: Jenkins received the failure payload via the webhook and instantly aborted the pipeline execution, successfully blocking the vulnerable application from proceeding to the Docker build phase.

SCA Validation: Independent runs of the Trivy stage confirmed successful identification of high/critical CVEs in outdated third-party Node modules (e.g., form-data, sqlite3).
