# Phase 13: Autonomous Self-Healing and Email Notification

## Objective

The objective of this phase is to implement an autonomous runtime self-healing engine that consumes Falco runtime security events, analyzes risk, generates remediation decisions, sends email alerts, and safely executes remediation only for controlled demo workloads.

This phase validates:

* Falco runtime event parsing
* Risk-based decision generation
* Email alert preview generation
* Real SMTP email alert sending
* Dry-run remediation mode
* Safe execute remediation mode
* Kubernetes pod remediation
* JSON and Markdown evidence generation

---

## Tool Used

| Tool / Component | Purpose |
|---|---|
| Python | Self-healing automation engine |
| Falco | Runtime security event source |
| Kubernetes | Runtime remediation target |
| kubectl | Pod validation and remediation |
| SMTP | Email alert sending |
| Gmail App Password | Secure SMTP authentication |
| JSON Report | Machine-readable evidence |
| Markdown Report | Human-readable evidence |

---

## Prerequisites

Before starting this phase, the following phases must be completed:

| Phase | Requirement | Status |
|---|---|---|
| Phase 11 | Monitoring and Observability | Completed |
| Phase 12 | Runtime Security with Falco | Completed |

Required running components:

```text
Kubernetes cluster: devsecops-cluster
Application namespace: devsecops
Runtime security: Falco
Monitoring stack: Prometheus, Grafana, Alertmanager
GitOps: Argo CD
```

---

## Step 1: Create Self-Healing Engine Structure

A new self-healing engine directory was created.

```text
self-healing-engine/
├── input/
│   └── .gitkeep
├── output/
│   └── .gitkeep
└── src/
    └── runtime_self_heal.py
```

The input and output directories are used for local runtime evidence.

---

## Step 2: Ignore Runtime Evidence and Secrets

Generated runtime evidence and local email secrets were excluded from GitHub.

`.gitignore` was updated with:

```text
self-healing-engine/input/*
!self-healing-engine/input/.gitkeep

self-healing-engine/output/*
!self-healing-engine/output/.gitkeep

self-healing-engine/.env
```

This prevents committing sensitive runtime evidence or SMTP credentials.

---

## Step 3: Implement Runtime Self-Healing Engine

The self-healing engine was implemented in:

```text
self-healing-engine/src/runtime_self_heal.py
```

The engine performs the following workflow:

```text
Read Falco runtime event evidence
↓
Extract namespace, pod, container, image, process, file, rule, and severity
↓
Classify event risk
↓
Generate remediation decision
↓
Generate email alert preview
↓
Optionally send real email alert
↓
Run in dry-run mode by default
↓
Execute safe remediation only when explicitly enabled
```

---

## Step 4: Safety Controls

The engine does not delete pods blindly.

Automated pod deletion is allowed only when all conditions are true:

```text
Namespace must be: devsecops
Detected event must be high risk
Action must be: DELETE_POD_IF_DEMO_LABEL_PRESENT
Pod must contain safety label: self-heal-demo=true
Execute mode must be explicitly enabled
```

Required safety label:

```text
self-heal-demo=true
```

This ensures that only controlled demo pods can be remediated automatically.

---

## Step 5: Initial Dry-Run Analysis

Falco runtime evidence from Phase 12 was copied into the self-healing input directory.

```bash
cp reports/phase-12-falco/falco-runtime-detection-evidence.txt \
  self-healing-engine/input/falco-runtime-detection-evidence.txt
```

The engine was executed in dry-run mode.

```bash
python3 self-healing-engine/src/runtime_self_heal.py
```

Verified result:

```text
Self-healing summary written to: self-healing-engine/output/self-healing-summary.json
Self-healing report written to: self-healing-engine/output/self-healing-report.md
Email alert preview written to: self-healing-engine/output/email-alert-preview.txt
Email sent: False
Email status: Email sending not requested. Email alert file generated only.
Events analyzed: 2
High-risk events: 1
Mode: dry-run
```

---

## Step 6: Create Controlled Self-Healing Test Pod

A temporary test pod was created with the required safety label.

```bash
kubectl run falco-selfheal-test \
  -n devsecops \
  --image=alpine \
  --restart=Never \
  --labels self-heal-demo=true \
  --command -- sh -c "sleep 300"
```

The pod was verified with labels:

```bash
kubectl get pod falco-selfheal-test -n devsecops --show-labels
```

Required label:

```text
self-heal-demo=true
```

---

## Step 7: Trigger Runtime Security Event

A safe suspicious action was executed inside the test container.

```bash
kubectl exec -n devsecops falco-selfheal-test -- sh -c "cat /etc/shadow >/dev/null 2>&1 || true"
```

Falco detected sensitive file access inside the container.

The event was captured into the self-healing input file:

```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco -c falco --since=5m \
  | grep -Ei "falco-selfheal-test|shadow|sensitive|warning|critical|notice" \
  > self-healing-engine/input/falco-runtime-detection-evidence.txt
```

---

## Step 8: Validate Dry-Run Remediation Decision

The engine was run again in dry-run mode.

```bash
python3 self-healing-engine/src/runtime_self_heal.py
```

Verified result:

```text
Events analyzed: 1
High-risk events: 1
Mode: dry-run
```

Generated decision:

```text
Rule: Sensitive file opened for reading by non-trusted program
Severity: warning
Namespace: devsecops
Pod: falco-selfheal-test
Container: falco-selfheal-test
Image: docker.io/library/alpine:latest
Process: cat
File: /etc/shadow
Risk Level: HIGH
Action: DELETE_POD_IF_DEMO_LABEL_PRESENT
Safe To Execute: True
```

Dry-run execution summary:

```text
Mode: dry-run
Executed: False
Check: Required safety label found: self-heal-demo=true
Check: Dry-run mode: would run `kubectl delete pod falco-selfheal-test -n devsecops`
```

---

## Step 9: Execute Safe Self-Healing Action

After dry-run validation, execute mode was used.

```bash
python3 self-healing-engine/src/runtime_self_heal.py --execute
```

Verified result:

```text
Events analyzed: 1
High-risk events: 1
Mode: execute
```

The suspicious demo pod was deleted by the self-healing engine.

Verification:

```bash
kubectl get pod falco-selfheal-test -n devsecops
```

Verified result:

```text
Error from server (NotFound): pods "falco-selfheal-test" not found
```

This confirms that the remediation action was executed successfully.

---

## Step 10: Email Alert Preview

The engine generated an email alert preview.

Generated file:

```text
self-healing-engine/output/email-alert-preview.txt
```

Email subject:

```text
[BLOCKED] DevSecOps Runtime Security Alert
```

The email alert includes:

```text
Detected rule
Severity
Namespace
Pod name
Container name
Process name
Sensitive file
Risk level
Recommended action
Execution mode
Remediation status
```

---

## Step 11: Real Email Alert Configuration

A safe example configuration file was added:

```text
self-healing-engine/.env.example
```

Example:

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-gmail-app-password

ALERT_EMAIL_FROM=your-email@gmail.com
ALERT_EMAIL_TO=security-team@example.com
```

The real `.env` file is local only and is ignored by Git.

---

## Step 12: Real Email Alert Verification

The self-healing engine was tested with real SMTP email notification enabled.

Command used:

```bash
set -a
source self-healing-engine/.env
set +a

python3 self-healing-engine/src/runtime_self_heal.py --send-email
```

Verified result:

```text
Self-healing summary written to: self-healing-engine/output/self-healing-summary.json
Self-healing report written to: self-healing-engine/output/self-healing-report.md
Email alert preview written to: self-healing-engine/output/email-alert-preview.txt
Email sent: True
Email status: Email alert sent successfully.
Events analyzed: 1
High-risk events: 1
Mode: dry-run
```

This confirms that the self-healing engine can send a real runtime security email alert when a high-risk Falco event is detected.

---

## Step 13: Generated Evidence Files

The engine generated the following local evidence files:

```text
self-healing-engine/output/self-healing-summary.json
self-healing-engine/output/self-healing-report.md
self-healing-engine/output/email-alert-preview.txt
```

These files are local runtime evidence and are not committed to GitHub.

---

## Step 14: GitHub Commits

Self-healing engine implementation commit:

```text
5ad23d7 feat: add autonomous runtime self-healing engine
```

Email configuration example commit:

```text
63ca127 chore: add self-healing email alert configuration example
```

---

## Autonomous Self-Healing Flow

```text
Falco detects suspicious runtime activity
↓
Falco writes event to logs
↓
Self-healing engine reads Falco evidence
↓
Engine extracts namespace, pod, container, process, file, and rule
↓
Engine classifies risk
↓
Engine generates remediation decision
↓
Engine generates email alert preview
↓
Engine sends real email alert when SMTP is enabled
↓
Engine checks safety controls
↓
Dry-run shows proposed remediation
↓
Execute mode deletes only demo-labeled suspicious pod
↓
JSON and Markdown reports are generated
```

---

## Evidence Collected

| Evidence | Result |
|---|---|
| Falco event parsed | Successful |
| Sensitive file detected | `/etc/shadow` |
| High-risk event count | 1 |
| Demo pod | falco-selfheal-test |
| Safety label | self-heal-demo=true |
| Dry-run remediation | Successful |
| Execute remediation | Successful |
| Pod deletion | Successful |
| Email preview | Generated |
| Real email alert | Sent successfully |
| JSON report | Generated |
| Markdown report | Generated |
| Implementation commit | 5ad23d7 |
| Email config commit | 63ca127 |

---

## Security and DevOps Value Added

This phase adds the following value:

* Converts runtime detection into automated response
* Adds safe self-healing capability
* Prevents blind remediation using namespace and label checks
* Supports dry-run validation before execution
* Sends real email alerts for high-risk runtime events
* Generates audit-ready JSON and Markdown reports
* Connects Falco runtime security with Kubernetes remediation
* Completes the self-healing platform capability
* Demonstrates practical autonomous DevSecOps response logic
