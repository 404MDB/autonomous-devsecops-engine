# Autonomous AI-Driven DevSecOps Engine

## Secure SSDLC and Cloud-Native Self-Healing Platform

## Project Overview

The **Autonomous AI-Driven DevSecOps Engine** is an end-to-end Secure Software Development Lifecycle platform built to demonstrate automated security, vulnerability management, AI-assisted security intelligence, Kubernetes GitOps deployment, runtime threat detection, and controlled autonomous self-healing response in a cloud-native environment.

The project secures a sample dummy UPI application across the complete delivery lifecycle using CI/CD security gates, security scanning tools, vulnerability reporting, SBOM generation, image signing, Kubernetes deployment, monitoring, runtime security detection, email notification, and safe automated remediation.

This project demonstrates how modern DevSecOps can move from simple CI/CD scanning to a complete security automation platform covering build-time, deploy-time, and runtime security.

---

## Objective

The objective of this project is to build a practical DevSecOps platform capable of:

* Automating CI/CD security workflows
* Detecting leaked secrets
* Performing static application security testing
* Scanning dependencies and container images
* Running dynamic application security testing
* Centralizing vulnerabilities in DefectDojo
* Generating SBOMs
* Signing and verifying container image artifacts
* Applying security gates
* Performing AI-assisted risk analysis
* Deploying applications to Kubernetes
* Managing Kubernetes delivery using GitOps
* Monitoring workloads using Prometheus and Grafana
* Detecting runtime threats using Falco
* Sending email alerts for runtime security events
* Performing safe autonomous self-healing actions for controlled demo workloads

---

## Final Project Status

```text
Project Status: Completed

Latest Completed Capability:
Autonomous Self-Healing and Email Notification

Final Outcome:
Falco detected suspicious runtime behavior, the self-healing engine analyzed the event, generated a risk decision, created evidence reports, sent an email alert, and safely deleted only the demo-labeled suspicious pod.
```

---

## Complete DevSecOps Flow

```text
GitHub Repository
↓
Jenkins CI/CD Pipeline
↓
TruffleHog Secret Scanning
↓
SonarQube SAST Analysis
↓
Trivy Filesystem and Container Scanning
↓
OWASP ZAP DAST
↓
DefectDojo Vulnerability Management
↓
Syft SBOM Generation
↓
Cosign Image Signing and Verification
↓
AI Security Intelligence Engine
↓
Kubernetes Deployment
↓
Argo CD GitOps Sync and Self-Healing
↓
Prometheus, Grafana, and Alertmanager Monitoring
↓
Falco Runtime Security Detection
↓
Autonomous Self-Healing Engine
↓
Email Security Alert
↓
Audit-Ready Evidence Reports
```

---

## Completed Phases

| Phase | Area | Tool / Technology | Status |
|---|---|---|---|
| Phase 1 | Environment Setup | WSL2, Ubuntu 24.04, Docker Desktop, VS Code Remote WSL | Completed |
| Phase 2 | CI/CD Foundation | Jenkins, GitHub, Docker | Completed |
| Phase 3 | SonarQube SAST Integration | SonarQube, SonarScanner | Completed |
| Phase 4 | Trivy SCA and Container Security Gate | Trivy | Completed |
| Phase 5 | OWASP ZAP DAST Integration | OWASP ZAP | Completed |
| Phase 6 | DefectDojo Vulnerability Management | DefectDojo | Completed |
| Phase 7 | SBOM and Supply Chain Security | Syft, Cosign | Completed |
| Phase 8 | AI Security Intelligence Layer | Python, Report Parser | Completed |
| Phase 9 | Kubernetes Deployment | kind, Kubernetes, kubectl | Completed |
| Phase 10 | GitOps with Argo CD | Argo CD, GitHub, Kustomize | Completed |
| Phase 11 | Monitoring and Observability | Prometheus, Grafana, Alertmanager | Completed |
| Phase 12 | Runtime Security | Falco | Completed |
| Phase 13 | Autonomous Self-Healing and Email Notification | Python, Falco, kubectl, SMTP | Completed |

---

## Completed Security Integrations

* WSL2 Ubuntu 24.04 development environment
* VS Code Remote WSL integration
* Docker Desktop with WSL integration
* Git and GitHub repository setup
* Jenkins CI/CD pipeline
* Docker integration with Jenkins
* TruffleHog secret scanning
* SonarQube static code analysis
* SonarQube Quality Gate integration
* Trivy vulnerability scanning
* Trivy CRITICAL vulnerability gate
* OWASP ZAP dynamic application security testing
* DefectDojo vulnerability management
* Automated Trivy report upload to DefectDojo
* Automated ZAP report upload to DefectDojo
* Syft CycloneDX SBOM generation
* Syft SPDX SBOM generation
* Cosign image signing
* Cosign signature verification
* AI Security Intelligence report parser
* AI-based release decision generation
* Kubernetes deployment using kind
* Argo CD GitOps synchronization
* Argo CD self-healing validation
* Prometheus monitoring
* Grafana dashboard access
* Alertmanager readiness
* Application `/metrics` endpoint
* Prometheus ServiceMonitor
* PrometheusRule alerting
* Falco runtime threat detection
* Autonomous self-healing engine
* Email alert notification
* Markdown and JSON evidence reports

---

## Toolchain

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
| Image Signing | Cosign |
| AI Security Analysis | Python Security Intelligence Engine |
| Kubernetes | kind, kubectl |
| GitOps | Argo CD |
| Monitoring | Prometheus, Grafana, Alertmanager |
| Runtime Security | Falco |
| Self-Healing | Python Automation Engine |
| Notification | SMTP Email Alert |

---

## Jenkins CI/CD Security Pipeline

```text
Checkout Code
↓
DevSecOps Environment Check
↓
TruffleHog Secrets Scan
↓
SonarQube Code Analysis
↓
SonarQube Quality Gate Check
↓
Docker Image Build
↓
Trivy JSON Vulnerability Report
↓
Syft SBOM Generation
↓
Cosign Image Signing and Verification
↓
OWASP ZAP DAST Scan
↓
Upload Trivy Report to DefectDojo
↓
Upload ZAP Report to DefectDojo
↓
AI Security Intelligence Analysis
↓
Trivy CRITICAL Vulnerability Gate
↓
Archive Reports and Evidence
```

---

## AI Security Intelligence Layer

The AI Security Intelligence layer analyzes security reports generated by the pipeline.

It processes:

```text
Trivy JSON report
OWASP ZAP XML report
CycloneDX SBOM report
Cosign verification report
```

It generates:

```text
ai-security-summary.json
ai-security-report.md
release-decision.txt
```

Verified release decision:

```text
Risk Level: CRITICAL
Release Decision: BLOCK_RELEASE
Reason: Critical vulnerabilities are present in the container image.
```

The AI Security Intelligence layer helps convert raw scanner output into risk-based security decisions that can be used by developers, security teams, and release reviewers.

---

## DefectDojo Vulnerability Management

DefectDojo is used as the centralized vulnerability management platform.

It provides:

* Centralized vulnerability tracking
* Severity-based prioritization
* Security finding deduplication
* Remediation tracking
* Audit-ready evidence
* Jenkins-based automated report upload

Completed DefectDojo integrations:

```text
Manual Trivy import
Manual OWASP ZAP import
Automated Jenkins Trivy upload
Automated Jenkins ZAP upload
```

---

## SBOM and Image Signing

The project generates SBOMs using Syft.

Generated formats:

```text
CycloneDX JSON
SPDX JSON
```

Cosign is used for image artifact signing and verification.

Verified result:

```text
Cosign Signature Verification: PASSED
Artifact: dummy-upi-app:latest
Result: Verified OK
```

This adds software supply chain visibility and helps verify that container artifacts are signed before being treated as trusted release evidence.

---

## Kubernetes and GitOps

The application is deployed to Kubernetes using a local kind cluster.

Kubernetes resources:

```text
Namespace: devsecops
Deployment: dummy-upi-app
Service: dummy-upi-service
Replicas: 2
```

Argo CD is used for GitOps deployment.

Verified Argo CD status:

```text
Application: dummy-upi-app
Sync Status: Synced
Health Status: Healthy
Self-Heal: Enabled
Prune: Enabled
```

Argo CD self-healing was validated by manually changing the replica count. Argo CD restored the deployment back to the Git-defined state.

This demonstrates cloud-native GitOps behavior in a local Kubernetes environment.

---

## Monitoring and Observability

The monitoring stack was deployed using kube-prometheus-stack.

Installed components:

```text
Prometheus
Grafana
Alertmanager
Prometheus Operator
kube-state-metrics
node-exporter
```

The dummy UPI application exposes metrics at:

```text
/metrics
```

Custom metric:

```text
dummy_upi_http_requests_total
```

Prometheus verified scrape result:

```text
up{namespace="devsecops",job="dummy-upi-service"} = 1
```

Application alert rules were added using PrometheusRule:

```text
DummyUPIAppDown
DummyUPIHighHttp5xxErrors
```

---

## Runtime Security with Falco

Falco was deployed as a Kubernetes DaemonSet.

Verified Falco status:

```text
Falco pod: 2/2 Running
DaemonSet: 1/1 Ready
Event source: syscall
Runtime engine: modern BPF probe
```

Falco detected suspicious runtime activity:

```text
Warning Sensitive file opened for reading by non-trusted program
file=/etc/shadow
process=cat
container_name=falco-test
k8s_pod_name=falco-test
k8s_ns_name=devsecops
```

This proves runtime threat detection is working inside the Kubernetes cluster.

---

## Autonomous Self-Healing and Email Notification

The self-healing engine reads Falco runtime security events and generates controlled automated remediation decisions.

Self-healing workflow:

```text
Falco detects suspicious runtime activity
↓
Self-healing engine parses the Falco event
↓
Engine extracts pod, namespace, container, process, file, and severity
↓
Engine classifies risk
↓
Engine generates an email alert
↓
Engine checks safety controls
↓
Dry-run mode shows proposed action
↓
Execute mode deletes only demo-labeled suspicious pods
```

Safety controls:

```text
Allowed namespace: devsecops
Required safety label: self-heal-demo=true
Default mode: dry-run
Execute mode must be explicitly enabled
```

Verified self-healing result:

```text
Events analyzed: 1
High-risk events: 1
Mode: execute
Suspicious pod: falco-selfheal-test
Result: Pod deleted successfully
```

Verified email alert result:

```text
Email sent: True
Email status: Email alert sent successfully.
```

This confirms that the project supports controlled autonomous response for runtime security events while preventing unsafe blind remediation.

---

## Cloud-Native Scope

This project is implemented in a local cloud-native lab environment.

Current environment:

```text
WSL2 Ubuntu 24.04
Docker Desktop
kind Kubernetes cluster
Local Jenkins
Local SonarQube
Local DefectDojo
Local Prometheus and Grafana
Local Falco deployment
```

The project is **cloud-native** because it uses containers, Kubernetes, GitOps, monitoring, runtime security, and self-healing automation.

The project is **not described as a cloud-hosted platform** because it is not currently deployed on AWS EKS, Azure AKS, or Google GKE.

---

## Repository Structure

```text
autonomous-devsecops-engine/
├── .gitignore
├── Jenkinsfile
├── README.md
├── ai-security-engine/
│   ├── input/
│   ├── output/
│   └── src/
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
│   ├── 11-ai-security-intelligence-layer.md
│   ├── 12-kubernetes-deployment.md
│   ├── 13-gitops-argocd.md
│   ├── 14-monitoring-observability.md
│   ├── 15-runtime-security-falco.md
│   └── 16-autonomous-self-healing.md
├── dummy-upi-app/
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   └── server.js
├── k8s/
│   ├── argocd/
│   ├── base/
│   ├── falco/
│   └── monitoring/
├── reports/
│   └── .gitkeep
├── screenshots/
│   └── .gitkeep
└── self-healing-engine/
    ├── .env.example
    ├── input/
    ├── output/
    └── src/
```

---

## Documentation

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
| `docs/10-sbom-and-supply-chain-security.md` | SBOM and Cosign supply chain security |
| `docs/11-ai-security-intelligence-layer.md` | AI security intelligence |
| `docs/12-kubernetes-deployment.md` | Kubernetes deployment |
| `docs/13-gitops-argocd.md` | Argo CD GitOps |
| `docs/14-monitoring-observability.md` | Prometheus, Grafana, and Alertmanager |
| `docs/15-runtime-security-falco.md` | Falco runtime security |
| `docs/16-autonomous-self-healing.md` | Autonomous self-healing and email notification |

---

## Security Gates

| Gate | Tool | Enforcement |
|---|---|---|
| Secret Gate | TruffleHog | Blocks leaked secrets |
| SAST Gate | SonarQube | Quality Gate validation |
| Vulnerability Gate | Trivy | Blocks CRITICAL vulnerabilities |
| DAST Evidence | OWASP ZAP | Generates runtime web security report |
| Supply Chain Evidence | Syft, Cosign | SBOM and image verification |
| AI Decision Gate | AI Security Engine | Generates release decision |
| Runtime Detection | Falco | Detects suspicious workload behavior |
| Self-Healing Safety Gate | Python Engine | Deletes only demo-labeled suspicious pods |

---

## Important Security Notes

* Real credentials are not committed to GitHub.
* Runtime evidence files are stored locally.
* Email credentials are stored only in `self-healing-engine/.env`.
* `.env.example` is provided only as a safe template.
* Generated reports under `reports/`, `ai-security-engine/output/`, and `self-healing-engine/output/` are ignored.
* Self-healing delete action works only when the required demo label is present.
* The project demonstrates controlled self-healing in a local Kubernetes lab, not unrestricted production remediation.

---

## Final Outcome

This project demonstrates a complete AI-driven DevSecOps lifecycle:

```text
Secure CI/CD
↓
Security Scanning
↓
Vulnerability Management
↓
SBOM and Image Signing
↓
AI Security Analysis
↓
Kubernetes Deployment
↓
GitOps Delivery
↓
Monitoring and Alerting
↓
Runtime Threat Detection
↓
Controlled Autonomous Self-Healing
↓
Email Security Notification
```

The final platform proves how security can be automated across build-time, deploy-time, and runtime stages of the software delivery lifecycle using cloud-native DevSecOps practices.
