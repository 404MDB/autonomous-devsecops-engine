# Phase 12: Runtime Security with Falco

## Objective

The objective of this phase is to implement Kubernetes runtime security monitoring using Falco.

This phase validates:

* Falco installation on Kubernetes
* Runtime threat detection
* Container activity monitoring
* Detection of suspicious file access
* Kubernetes workload visibility
* Runtime evidence collection
* Foundation for autonomous self-healing actions

---

## Tool Used

| Tool / Component | Purpose |
|---|---|
| Falco | Runtime threat detection |
| Helm | Falco installation |
| Kubernetes | Runtime environment |
| kind | Local Kubernetes cluster |
| kubectl | Kubernetes management |
| Falco rules | Detection logic for suspicious runtime behavior |
| Falco logs | Runtime security evidence |

---

## Prerequisites

Before starting this phase, the following phases must be completed:

| Phase | Requirement | Status |
|---|---|---|
| Phase 9 | Kubernetes Deployment | Completed |
| Phase 10 | GitOps with Argo CD | Completed |
| Phase 11 | Monitoring and Observability | Completed |

The Kubernetes application must already be running:

```text
Namespace: devsecops
Deployment: dummy-upi-app
Service: dummy-upi-service
```

---

## Step 1: Add Falco Helm Repository

The Falco Helm repository was added.

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts

helm repo update

helm search repo falcosecurity/falco | head
```

---

## Step 2: Create Falco Namespace

A dedicated namespace was created for Falco.

```bash
kubectl create namespace falco --dry-run=client -o yaml | kubectl apply -f -
```

Verified result:

```text
namespace/falco created
```

---

## Step 3: Install Falco

Falco was installed using Helm.

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace falco \
  --set tty=true \
  --wait \
  --timeout 10m
```

Verified result:

```text
NAME: falco
NAMESPACE: falco
STATUS: deployed
REVISION: 1
```

---

## Step 4: Verify Falco Pods

```bash
kubectl get pods -n falco
```

Verified result:

```text
NAME          READY   STATUS    RESTARTS   AGE
falco-bshmg   2/2     Running   0          9m
```

This confirms that the Falco pod is running successfully.

---

## Step 5: Verify Falco DaemonSet

```bash
kubectl get daemonset -n falco
```

Verified result:

```text
NAME    DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE
falco   1         1         1       1            1
```

This confirms that the Falco DaemonSet is healthy and running on the Kubernetes node.

---

## Step 6: Verify Falco Helm Release

```bash
helm list -n falco
```

Verified result:

```text
NAME    NAMESPACE   REVISION   STATUS     CHART       APP VERSION
falco   falco       1          deployed   falco-9.1.0 0.44.1
```

---

## Step 7: Verify Falco Runtime Engine

Falco logs were checked to confirm rule loading and runtime event monitoring.

```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco -c falco --tail=80
```

Verified important log entries:

```text
Falco version: 0.44.1
Falco initialized with configuration files
Loading rules from: /etc/falco/falco_rules.yaml
Loaded event sources: syscall
Enabled event sources: syscall
Opening 'syscall' source with modern BPF probe
```

This confirms that Falco successfully started and enabled syscall-based runtime monitoring.

---

## Step 8: Create Runtime Test Pod

A temporary Alpine pod was created to safely generate a runtime security event.

```bash
kubectl run falco-test \
  -n devsecops \
  --image=alpine \
  --restart=Never \
  --command -- sh -c "sleep 300"
```

The test pod was verified:

```bash
kubectl wait --for=condition=Ready pod/falco-test -n devsecops --timeout=120s

kubectl get pod falco-test -n devsecops
```

---

## Step 9: Trigger Suspicious Runtime Activity

A safe test command was executed inside the container to simulate suspicious access to a sensitive file.

```bash
kubectl exec -n devsecops falco-test -- sh -c "cat /etc/shadow >/dev/null 2>&1 || true"
```

This action does not modify the system. It only attempts to read a sensitive file inside the temporary test container.

---

## Step 10: Verify Falco Detection

Falco logs were searched for the generated runtime event.

```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco -c falco --since=10m \
  | grep -Ei "falco-test|shadow|sensitive|shell|terminal|notice|warning|critical" || true
```

Verified Falco detection:

```text
Warning Sensitive file opened for reading by non-trusted program
file=/etc/shadow
process=cat
container_name=falco-test
container_image_repository=docker.io/library/alpine
container_image_tag=latest
k8s_pod_name=falco-test
k8s_ns_name=devsecops
```

This proves that Falco detected suspicious runtime behavior inside a Kubernetes container.

---

## Step 11: Additional Runtime Event Observed

Falco also detected platform-level Kubernetes activity.

```text
Notice Unexpected connection to K8s API Server from container
container_name=argocd-applicationset-controller
container_image_repository=quay.io/argoproj/argocd
k8s_pod_name=argocd-applicationset-controller
k8s_ns_name=argocd
```

This confirms that Falco is not only monitoring the application namespace, but also observing Kubernetes platform activity.

---

## Step 12: Clean Up Test Pod

After the runtime detection test, the temporary pod was removed.

```bash
kubectl delete pod falco-test -n devsecops
```

If the pod was already removed, Kubernetes returned:

```text
Error from server (NotFound): pods "falco-test" not found
```

This is acceptable because the runtime detection evidence was already captured.

---

## Step 13: Save Runtime Evidence Locally

Evidence was saved locally under the reports directory.

```bash
mkdir -p reports/phase-12-falco

kubectl get pods -n falco -o wide > reports/phase-12-falco/falco-pods.txt

kubectl get daemonset -n falco > reports/phase-12-falco/falco-daemonset.txt

helm list -n falco > reports/phase-12-falco/falco-helm-release.txt

kubectl logs -n falco -l app.kubernetes.io/name=falco -c falco --since=30m \
  | grep -Ei "falco-test|shadow|sensitive|warning|critical|notice" \
  > reports/phase-12-falco/falco-runtime-detection-evidence.txt
```

The evidence files are kept locally and are not committed to GitHub.

---

## Step 14: Add Reproducible Falco Configuration

A Falco values file was created for GitHub.

File:

```text
k8s/falco/values.yaml
```

Content:

```yaml
tty: true

falco:
  jsonOutput: false
  priority: debug

falcoctl:
  artifact:
    install:
      enabled: true
    follow:
      enabled: true
```

This file documents the Falco runtime security configuration used in the project.

---

## Step 15: Commit Falco Configuration

The Falco configuration was committed and pushed to GitHub.

```bash
git add k8s/falco/values.yaml

git commit -m "feat: add Falco runtime security configuration"

git push origin main
```

Verified commit:

```text
efb779b feat: add Falco runtime security configuration
```

---

## Runtime Security Flow

```text
Kubernetes workload runs inside cluster
↓
Falco runs as DaemonSet on Kubernetes node
↓
Falco monitors syscall activity
↓
Suspicious file access occurs inside container
↓
Falco rule detects sensitive file read
↓
Falco writes runtime security event to logs
↓
Evidence is collected for security review
↓
Future self-healing phase can consume Falco events
```

---

## Evidence Collected

| Evidence | Result |
|---|---|
| Falco namespace | Created |
| Falco Helm release | Deployed |
| Falco chart | falco-9.1.0 |
| Falco app version | 0.44.1 |
| Falco pod | 2/2 Running |
| Falco DaemonSet | 1/1 Ready |
| Falco rules | Loaded |
| Event source | syscall |
| Runtime engine | modern BPF probe |
| Test pod | falco-test |
| Runtime test | Sensitive file read |
| Detection result | Warning generated |
| Detected file | /etc/shadow |
| Detected process | cat |
| Detected namespace | devsecops |
| Git commit | efb779b |

---

## Security and DevOps Value Added

This phase adds the following value:

* Adds runtime security monitoring to Kubernetes
* Detects suspicious container behavior after deployment
* Identifies sensitive file access inside containers
* Provides runtime security evidence for audit and analysis
* Extends DevSecOps coverage from CI/CD scanning to live workload monitoring
* Complements Trivy, OWASP ZAP, DefectDojo, Prometheus, and Alertmanager
* Creates the runtime detection foundation needed for autonomous self-healing
* Prepares the project for automated remediation based on security events
