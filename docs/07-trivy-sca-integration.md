# Phase 4: Software Composition Analysis (SCA) & Quality Gate Enforcement

## Objective

Implement Software Composition Analysis using Trivy and enforce security validation through Jenkins by integrating SonarQube Quality Gate checks and container vulnerability scanning.

This phase ensures that vulnerable dependencies, insecure container layers, and failed quality/security checks are detected before the application moves further in the CI/CD pipeline.

---

## Prerequisites

* Phase 3 completed: SonarQube SAST integration.
* Node.js dummy UPI gateway application available.
* Dockerized application build process implemented.
* Jenkins configured with Docker Outside of Docker architecture.
* SonarQube webhook configured for Jenkins Quality Gate callback.

---

## Step-by-Step Configuration

## Step 1: Quality Gate Webhook Configuration

To allow SonarQube to actively communicate analysis results back to the CI/CD pipeline, a webhook was established.

Webhook endpoint:

```text id="9v63ev"
http://172.17.0.1:8080/sonarqube-webhook/
```

This establishes an asynchronous communication line from the SonarQube container back to the Jenkins controller across the Docker bridge network.

The webhook allows Jenkins to receive the final Quality Gate result after SonarQube completes static analysis.

---

## Step 2: Jenkins NodeJS Runtime Injection

To prevent runtime parsing errors during JavaScript SAST analysis, the official NodeJS Jenkins plugin was installed and configured.

The NodeJS tool was injected directly into the Jenkins declarative pipeline using the `tools` block:

```groovy id="y7o6tc"
tools {
    nodejs 'NodeJS'
}
```

This ensures the SonarScanner can successfully execute JavaScript analysis for the Node.js application.

---

## Step 3: SCA Implementation with Trivy

Trivy was integrated to scan the resulting Docker image for:

* OS-level vulnerabilities
* Node.js dependency vulnerabilities
* Third-party package CVEs
* Container image security issues

Trivy is executed dynamically as an ephemeral Docker container.

This avoids installing Trivy directly on the Jenkins controller and keeps the CI/CD environment clean.

Pipeline implementation:

```groovy id="v9b85k"
stage('SCA: Trivy Container Scan') {
    steps {
        echo 'Summoning Trivy to scan the application image...'
        sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 1 --severity CRITICAL dummy-upi-app:latest'
    }
}
```

The Trivy scan uses the Docker socket because Jenkins follows a Docker Outside of Docker architecture.

---

## Step 4: Trivy Security Enforcement Policy

The Trivy scan is configured with the following enforcement flags:

```bash id="4ntd0y"
--exit-code 1 --severity CRITICAL
```

Meaning:

* If CRITICAL vulnerabilities are detected, the Jenkins build fails.
* If no CRITICAL vulnerabilities are detected, the pipeline continues.
* Lower severity vulnerabilities can be reviewed without immediately blocking academic development.

This creates a practical security gate for dependency and container image scanning.

---

## Step 5: Quality Gate Enforcement

A Jenkins Quality Gate stage was added immediately after SonarQube SAST analysis.

Initial enforcement configuration:

```groovy id="e0fksv"
stage('Quality Gate Check') {
    steps {
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

This configuration was used to verify strict DevSecOps enforcement.

When SonarQube evaluated the vulnerable application and failed the Quality Gate, Jenkins successfully aborted the pipeline and prevented the application from proceeding to the Docker build stage.

---

## Current Quality Gate Configuration

During active academic development, the Quality Gate has been temporarily changed to non-blocking mode:

```groovy id="solzft"
stage('Quality Gate Check') {
    steps {
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: false
        }
    }
}
```

Reason:

The project is still under active development, documentation, and tool integration. Keeping the Quality Gate non-blocking allows later stages such as Docker build, Trivy scanning, and OWASP ZAP DAST scanning to execute for demonstration and evidence collection.

Production recommendation:

```groovy id="06bcc5"
waitForQualityGate abortPipeline: true
```

In a production-grade DevSecOps pipeline, the Quality Gate should be restored to blocking mode.

---

## Verification and Outcomes

## SAST Execution

SonarScanner successfully analyzed the Node.js source code.

Earlier analysis identified security hotspots and quality concerns, including:

* Hardcoded cryptographic key patterns
* SQL injection risk areas
* Missing or low test coverage

These findings were used to validate SonarQube security analysis and Quality Gate enforcement.

---

## Quality Gate Enforcement Validation

The initial blocking configuration successfully verified that Jenkins can stop the pipeline when SonarQube Quality Gate fails.

This confirmed that the Jenkins-SonarQube webhook integration was working correctly.

Outcome:

```text id="czl71r"
Quality Gate failed
↓
Jenkins received webhook callback
↓
Pipeline aborted successfully
```

This proved that strict Quality Gate enforcement can be enabled when required.

---

## SCA Validation

Trivy successfully scanned the Docker image and detected vulnerable dependencies during earlier validation runs.

Examples of vulnerable dependency areas included:

* Outdated Node.js packages
* Vulnerable third-party modules
* Container image package vulnerabilities

After remediation, vulnerable dependencies were updated and the image was hardened.

Current Trivy enforcement remains active for CRITICAL vulnerabilities.

---

## Current Verified Pipeline Status

The latest Jenkins pipeline successfully completed all active stages, including:

* Source checkout
* Environment validation
* TruffleHog secrets scan
* SonarQube analysis
* Quality Gate check in non-blocking mode
* Docker image build
* Trivy container scan
* OWASP ZAP DAST scan
* Artifact archival
* Cleanup

Latest build result:

```text id="cbuy7y"
Finished: SUCCESS
```

This confirms that the SCA and pipeline security stages are currently stable after remediation.

---

## Security Value Added

This phase adds supply chain security and quality gate enforcement to the DevSecOps pipeline.

Benefits:

* Detects vulnerable third-party dependencies.
* Detects vulnerable OS packages inside the Docker image.
* Blocks CRITICAL vulnerabilities using Trivy.
* Validates SonarQube Quality Gate integration.
* Proves that Jenkins can enforce pipeline abortion when required.
* Supports both academic demonstration and production-grade enforcement design.
* Strengthens the Secure Software Development Lifecycle.

---

## Current Status

Phase 4 — Software Composition Analysis and Quality Gate Enforcement: COMPLETE

Current implementation status:

* Trivy SCA and container scanning are implemented.
* CRITICAL vulnerability blocking is enabled through Trivy.
* SonarQube Quality Gate integration is implemented.
* Quality Gate is temporarily configured as non-blocking using `abortPipeline: false`.
* Quality Gate can be restored to blocking mode by changing `abortPipeline` back to `true`.

Production hardening action:

Before presenting this as a production pipeline, restore:

```groovy id="acb023"
waitForQualityGate abortPipeline: true
```
