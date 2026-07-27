# Autonomous DevSecOps Engine

## Project Overview

The **Autonomous AI-Driven DevSecOps Engine** is an end-to-end DevSecOps platform that integrates Secure Software Development Life Cycle practices, CI/CD automation, container security, vulnerability management, AI-assisted security analysis, and future autonomous remediation.

The project demonstrates how modern software delivery pipelines can automatically build, scan, analyze, track, and improve application security before deployment.

---

## Objective

To build an automated DevSecOps platform capable of:

* Continuous Integration and Delivery
* Secret scanning
* Static Application Security Testing
* Dependency and container vulnerability scanning
* Dynamic Application Security Testing
* Centralized vulnerability management
* AI-assisted security analysis
* Risk prioritization and remediation guidance
* Future autonomous remediation and self-healing

---

## Current Progress

### Completed

| Phase | Status |
|---|---|
| Phase 1: Environment Setup | Completed |
| Phase 2: Jenkins CI/CD Foundation | Completed |
| Phase 3: SonarQube SAST Integration | Completed |
| Phase 4: Trivy SCA and Container Scanning | Completed |
| Phase 5: OWASP ZAP DAST Integration | Completed |
| Phase 6: DefectDojo Vulnerability Management | Manual Import Completed |

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
* Trivy container vulnerability scanning
* OWASP ZAP dynamic application security testing
* DefectDojo vulnerability management dashboard

---

## DefectDojo Manual Import Result

DefectDojo was configured as the centralized vulnerability management platform.

Imported tests:

| Scan Tool | Test ID | Findings |
|---|---:|---:|
| Trivy Scan | 1 | 81 |
| OWASP ZAP Scan | 2 | 6 |
| Total | - | 87 |

Severity summary:

| Severity | Count |
|---|---:|
| Critical | 2 |
| High | 29 |
| Medium | 25 |
| Low | 30 |
| Info | 1 |
| Total Active Findings | 87 |

---

## In Progress

* Phase 6 Jenkins automation for automatic DefectDojo upload
* Phase 7: SBOM and Supply Chain Security

---

## Upcoming

* AI Security Intelligence Layer
* Kubernetes migration
* GitOps workflow
* Monitoring and observability
* Runtime security
* Autonomous self-healing engine

---

## Repository Structure

```text
autonomous-devsecops-engine/
├── Jenkinsfile
├── README.md
├── docs/
├── docker/
├── dummy-upi-app/
├── reports/
└── screenshots/
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
| `docs/project-status.md` | Overall project status |

---

## Current Architecture Flow

```text
Developer
↓
Windows 11 + WSL2 Ubuntu + VS Code
↓
GitHub Repository
↓
Jenkins CI/CD Pipeline
↓
Docker Image Build
↓
Security Scanning Tools
    ├── TruffleHog: Secret Scanning
    ├── SonarQube: SAST
    ├── Trivy: SCA and Container Scanning
    └── OWASP ZAP: DAST
↓
Security Reports
↓
DefectDojo Vulnerability Management
↓
AI Security Intelligence Layer
↓
Risk Prioritization and Remediation Guidance
↓
Future Autonomous Self-Healing
```

---

## Final Project Vision

The final goal of this project is to create an AI-driven DevSecOps platform that can automatically scan, manage, analyze, prioritize, and eventually help remediate security vulnerabilities across the software delivery lifecycle.
