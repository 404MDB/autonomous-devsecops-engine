# Autonomous AI-Driven DevSecOps Engine

## Project Overview

The **Autonomous AI-Driven DevSecOps Engine** is an end-to-end Secure SSDLC and cloud self-healing platform built to demonstrate automated security controls across the complete software delivery lifecycle.

The project integrates CI/CD automation, secrets detection, static code analysis, vulnerability scanning, dynamic application security testing, vulnerability management, SBOM generation, image signing, security gate enforcement, and AI-assisted security analysis.

The next major phase adds an **AI Security Intelligence Layer** to analyze scan reports, summarize vulnerabilities, prioritize risks, recommend remediation, and support secure release decisions.

---

## Objective

To build an automated DevSecOps platform capable of:

* Continuous Integration and Delivery
* Secret scanning
* Static Application Security Testing
* Dependency and container vulnerability scanning
* Dynamic Application Security Testing
* Centralized vulnerability management
* SBOM generation
* Image artifact signing and verification
* Security gate enforcement
* AI-assisted security analysis
* Risk prioritization and remediation guidance
* Future autonomous remediation and self-healing

---

## Current Status

```text
Current Completed Phase: Phase 7
Completed Area: SBOM and Supply Chain Security
Current Result: Jenkins SBOM generation and Cosign verification completed
Latest Jenkins Result: Expected failure at Trivy CRITICAL gate
Next Phase: AI Security Intelligence Layer
```

The latest Jenkins pipeline may fail at the final Trivy CRITICAL vulnerability gate because CRITICAL vulnerabilities are intentionally blocked by the pipeline.

This confirms that the security gate is working as expected.

---

## Completed Phases

| Phase | Area | Tool / Technology | Status |
|---|---|---|---|
| Phase 1 | Environment Setup | WSL2, Ubuntu 24.04, Docker Desktop, VS Code Remote WSL | Completed |
| Phase 2 | CI/CD Foundation | Jenkins, GitHub, Docker Outside of Docker | Completed |
| Phase 3 | Secrets Detection and SAST | TruffleHog, SonarQube | Completed |
| Phase 4 | Vulnerability Scanning and Security Gates | Trivy, SonarQube Quality Gate | Completed |
| Phase 5 | Dynamic Application Security Testing | OWASP ZAP | Completed |
| Phase 6 | Vulnerability Management | DefectDojo | Completed |
| Phase 7 | SBOM and Supply Chain Security | Syft, Cosign | Completed |

---

## Completed Security Integrations

* WSL2 Ubuntu 24.04 development environment
* VS Code Remote WSL integration
* Docker Desktop with WSL integration
* Git and GitHub repository setup
* Jenkins CI/CD pipeline
* Docker socket integration with Jenkins
* TruffleHog secrets scanning
* SonarQube static code analysis
* SonarQube Quality Gate integration
* Trivy JSON vulnerability reporting
* Trivy CRITICAL vulnerability gate
* OWASP ZAP dynamic application security testing
* DefectDojo vulnerability management
* Automated Trivy report upload to DefectDojo
* Automated ZAP report upload to DefectDojo
* Syft CycloneDX SBOM generation
* Syft SPDX SBOM generation
* Cosign image artifact signing
* Cosign signature verification
* Jenkins security artifact archival
* Docker cleanup after pipeline execution

---

## Current CI/CD Security Pipeline

```text
GitHub Repository
↓
Jenkins SCM Checkout
↓
DevSecOps Environment Check
↓
TruffleHog Secrets Scan
↓
SonarQube SAST Analysis
↓
SonarQube Quality Gate Check
↓
Docker Image Build
↓
Trivy JSON Vulnerability Report
↓
Syft SBOM Generation
↓
Cosign Image Artifact Signing and Verification
↓
OWASP ZAP DAST Scan
↓
Upload Trivy Report to DefectDojo
↓
Upload ZAP Report to DefectDojo
↓
Trivy CRITICAL Vulnerability Gate
↓
Jenkins Artifact Archival and Cleanup
```

---

## Current Toolchain

| Category | Tool |
|---|---|
| Version Control | GitHub |
| CI/CD | Jenkins |
| Containerization | Docker |
| Secret Scanning | TruffleHog |
| SAST | SonarQube |
| Vulnerability Scanning | Trivy |
| DAST | OWASP ZAP |
| Vulnerability Management | DefectDojo |
| SBOM Generation | Syft |
| Image Signing and Verification | Cosign |

---

## DefectDojo Integration Status

DefectDojo is configured as the centralized vulnerability management platform.

Completed DefectDojo work:

```text
DefectDojo deployed locally
Academic Capstone organization created
Autonomous AI-Driven DevSecOps Engine asset created
CI/CD engagement created
Manual Trivy report import completed
Manual ZAP report import completed
Jenkins automated Trivy report upload completed
Jenkins automated ZAP report upload completed
```

DefectDojo is used for:

* Centralized vulnerability tracking
* Security finding deduplication
* Severity-based prioritization
* Remediation tracking
* Audit-ready evidence collection

---

## Latest SBOM Evidence

Syft generated two SBOM reports for the Docker image.

Generated SBOM files:

```text
reports/sbom/dummy-upi-app-cyclonedx.json
reports/sbom/dummy-upi-app-spdx.json
```

Verified Jenkins result:

```text
dummy-upi-app-cyclonedx.json   1.7M
dummy-upi-app-spdx.json        3.3M
```

SBOM formats generated:

| SBOM Format | Purpose | Status |
|---|---|---|
| CycloneDX | Component inventory and security workflows | Generated |
| SPDX | Package and license metadata | Generated |

---

## Latest Cosign Evidence

Cosign image artifact signing and verification was completed successfully.

Generated Cosign evidence files:

```text
reports/cosign/cosign-verify-raw-output.txt
reports/cosign/dummy-upi-app-image.sha256
reports/cosign/dummy-upi-app-image.sigstore.json
reports/cosign/dummy-upi-app-signature-verification.txt
```

Verified result:

```text
Cosign Signature Verification: PASSED
Artifact: dummy-upi-app:latest
Signed Artifact Type: Docker image archive
Bundle: reports/cosign/dummy-upi-app-image.sigstore.json
Checksum: reports/cosign/dummy-upi-app-image.sha256
Public Key Credential: cosign-public-key
Result: Verified OK
```

---

## Latest Trivy Gate Result

Trivy container scanning is configured as the final security gate.

Current enforcement:

```bash
--exit-code 1 --severity CRITICAL
```

Latest final gate result:

```text
dummy-upi-app:latest (debian 12.13)
Total: 7 (CRITICAL: 7)

Node.js (node-pkg)
Total: 2 (CRITICAL: 2)

Finished: FAILURE
```

This is expected behavior because the pipeline blocks unsafe images when CRITICAL vulnerabilities are detected.

---

## Repository Structure

```text
autonomous-devsecops-engine/
├── .gitignore
├── Jenkinsfile
├── README.md
├── docker/
│   └── jenkins/
├── docs/
│   ├── 01-wsl2-installation.md
│   ├── 02-vscode-and-wsl-integration.md
│   ├── 03-docker-installation.md
│   ├── 04-jenkins-installation.md
│   ├── 05-github-integration.md
│   ├── 06-sonarqube-integration.md
│   ├── 07-trivy-sca-integration.md
│   ├── 08-owasp-zap-dast-integration.md
│   ├── 09-defectdojo-vulnerability-management.md
│   ├── 10-sbom-and-supply-chain-security.md
│   └── project-status.md
├── dummy-upi-app/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   └── server.js
├── reports/
│   └── .gitkeep
└── screenshots/
    └── .gitkeep
```

---

## Documentation

Phase-wise documentation is maintained inside the `docs/` directory.

| Document | Description |
|---|---|
| `docs/01-wsl2-installation.md` | WSL2 setup |
| `docs/02-vscode-and-wsl-integration.md` | VS Code and WSL integration |
| `docs/03-docker-installation.md` | Docker setup |
| `docs/04-jenkins-installation.md` | Jenkins setup |
| `docs/05-github-integration.md` | GitHub integration |
| `docs/06-sonarqube-integration.md` | SonarQube SAST integration |
| `docs/07-trivy-sca-integration.md` | Trivy SCA and container scanning |
| `docs/08-owasp-zap-dast-integration.md` | OWASP ZAP DAST integration |
| `docs/09-defectdojo-vulnerability-management.md` | DefectDojo vulnerability management |
| `docs/10-sbom-and-supply-chain-security.md` | Syft SBOM and Cosign supply chain security |
| `docs/project-status.md` | Overall project status |

---

## In Progress

The next phase is:

```text
Phase 8: AI Security Intelligence Layer
```

This phase will add AI-assisted security analysis by parsing scan reports and generating risk-based security summaries.

Planned capabilities:

* Parse Trivy JSON reports
* Parse OWASP ZAP reports
* Parse SBOM metadata
* Summarize vulnerabilities
* Prioritize risks
* Recommend remediation
* Generate release decision summaries
* Prepare the foundation for autonomous security actions

---

## Upcoming Roadmap

| Phase | Area | Planned Tool |
|---|---|---|
| Phase 8 | AI Security Intelligence | Python, Local AI, Report Parser |
| Phase 9 | Kubernetes Deployment | Kubernetes |
| Phase 10 | GitOps | Argo CD |
| Phase 11 | Monitoring and Observability | Prometheus, Grafana, Alertmanager |
| Phase 12 | Runtime Security | Falco |
| Phase 13 | Autonomous Self-Healing | Automation Scripts, AI-assisted Recovery |

---

## Final Project Vision

The final version of this project will demonstrate a complete AI-driven DevSecOps lifecycle:

```text
Code Commit
↓
Automated CI/CD Security Pipeline
↓
Secrets, SAST, SCA, Container, DAST Scanning
↓
SBOM Generation and Image Signing
↓
Centralized Vulnerability Management
↓
AI Risk Analysis and Remediation Recommendation
↓
Kubernetes GitOps Deployment
↓
Monitoring and Runtime Security
↓
Autonomous Self-Healing Actions
```

The final goal is to create an AI-driven DevSecOps platform that can automatically scan, manage, analyze, prioritize, and eventually help remediate security vulnerabilities across the software delivery lifecycle.
