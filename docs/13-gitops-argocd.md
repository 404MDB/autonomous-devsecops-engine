# Phase 10: GitOps with Argo CD

## Objective

The objective of this phase is to implement GitOps-based Kubernetes deployment using Argo CD.

In this phase, Argo CD is configured to continuously monitor the GitHub repository and automatically synchronize Kubernetes manifests from the repository to the Kubernetes cluster.

This phase validates:

* Argo CD installation on Kubernetes
* GitOps deployment from GitHub
* Automated synchronization
* Kubernetes desired-state enforcement
* Drift detection
* Self-healing deployment behavior

---

## Tool Used

| Tool / Component | Purpose |
|---|---|
| Argo CD | GitOps continuous delivery for Kubernetes |
| Kubernetes | Target deployment platform |
| kind | Local Kubernetes cluster |
| kubectl | Kubernetes command-line management |
| GitHub | Source of truth for Kubernetes manifests |
| Kustomize | Applies Kubernetes base manifests |
| Argo CD Application | Defines GitOps sync configuration |

---

## Prerequisites

Before starting this phase, the following phases must be completed:

| Phase | Requirement | Status |
|---|---|---|
| Phase 8 | AI Security Intelligence Layer | Completed |
| Phase 9 | Kubernetes Deployment | Completed |

The Kubernetes deployment must already exist inside the cluster:

```text
Namespace: devsecops
Deployment: dummy-upi-app
Service: dummy-upi-service
Replicas: 2
```

The Kubernetes manifests must already exist in GitHub:

```text
k8s/base/
├── deployment.yaml
├── kustomization.yaml
├── namespace.yaml
└── service.yaml
```

---

## Step 1: Verify Kubernetes Cluster

The current Kubernetes cluster was verified before installing Argo CD.

```bash
kubectl get nodes
```

Verified result:

```text
NAME                              STATUS   ROLES           VERSION
devsecops-cluster-control-plane   Ready    control-plane   v1.31.0
```

---

## Step 2: Install Argo CD

Argo CD was installed into a dedicated namespace.

```bash
kubectl create namespace argocd

kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

The Argo CD pods were verified:

```bash
kubectl get all -n argocd
```

Verified result:

```text
pod/argocd-application-controller-0                     1/1 Running
pod/argocd-applicationset-controller                    1/1 Running
pod/argocd-dex-server                                   1/1 Running
pod/argocd-notifications-controller                     1/1 Running
pod/argocd-redis                                        1/1 Running
pod/argocd-repo-server                                  1/1 Running
pod/argocd-server                                       1/1 Running
```

Important Argo CD services:

```text
service/argocd-server
service/argocd-repo-server
service/argocd-redis
service/argocd-applicationset-controller
```

---

## Step 3: Access Argo CD UI

Argo CD server was exposed locally using port forwarding.

```bash
kubectl port-forward svc/argocd-server -n argocd 8082:443
```

Argo CD UI was accessed from the browser:

```text
https://localhost:8082
```

Initial admin password was retrieved using:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo
```

Login details:

```text
Username: admin
Password: Initial password from Kubernetes secret
```

---

## Step 4: Create Argo CD Application Manifest

A dedicated Argo CD application manifest was created.

File created:

```text
k8s/argocd/application.yaml
```

Content:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: dummy-upi-app
  namespace: argocd
  labels:
    app.kubernetes.io/name: dummy-upi-app
    app.kubernetes.io/part-of: autonomous-devsecops-engine
    app.kubernetes.io/component: gitops
spec:
  project: default

  source:
    repoURL: https://github.com/404MDB/autonomous-devsecops-engine.git
    targetRevision: main
    path: k8s/base

  destination:
    server: https://kubernetes.default.svc
    namespace: devsecops

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Key configuration:

| Field | Value |
|---|---|
| Application Name | dummy-upi-app |
| Argo CD Namespace | argocd |
| Git Repository | GitHub repository |
| Target Branch | main |
| Manifest Path | k8s/base |
| Destination Namespace | devsecops |
| Automated Sync | Enabled |
| Prune | Enabled |
| Self-Heal | Enabled |

---

## Step 5: Commit Argo CD Manifest

The Argo CD application manifest was committed and pushed to GitHub.

```bash
git add k8s/argocd/application.yaml

git commit -m "feat: add Argo CD application manifest"

git push origin main
```

Verified commit:

```text
5532924 feat: add Argo CD application manifest
```

---

## Step 6: Apply Argo CD Application

The Argo CD Application resource was applied to the Kubernetes cluster.

```bash
kubectl apply -f k8s/argocd/application.yaml
```

Verified result:

```text
application.argoproj.io/dummy-upi-app unchanged
```

---

## Step 7: Verify Argo CD Sync Status

Argo CD application status was checked.

```bash
kubectl get applications -n argocd

kubectl get application dummy-upi-app -n argocd
```

Verified result:

```text
NAME            SYNC STATUS   HEALTH STATUS
dummy-upi-app   Synced        Healthy
```

The sync and health status were also checked using JSONPath.

```bash
kubectl get application dummy-upi-app -n argocd \
  -o jsonpath='{.status.sync.status}{"\n"}{.status.health.status}{"\n"}'
```

Verified result:

```text
Synced
Healthy
```

---

## Step 8: Verify Argo CD Source Configuration

The Argo CD application configuration was inspected.

```bash
kubectl describe application dummy-upi-app -n argocd | grep -A20 -E "Sync Status|Health Status|Repo|Path|Revision"
```

Verified configuration:

```text
Path:             k8s/base
Repo URL:         https://github.com/404MDB/autonomous-devsecops-engine.git
Target Revision:  main
Sync Policy:
  Automated:
    Prune:      true
    Self Heal:  true
Sync Options:
  CreateNamespace=true
```

Verified sync result:

```text
Message: successfully synced (all tasks run)
Phase: Succeeded
Source Type: Kustomize
Status: Synced
Health Status: Healthy
```

---

## Step 9: Verify Kubernetes Application State

The Kubernetes application managed by Argo CD was verified.

```bash
kubectl get all -n devsecops
```

Verified result:

```text
NAME                                 READY   STATUS    RESTARTS      AGE
pod/dummy-upi-app-56bdd4dcc4-8vvmf   1/1     Running   1             2d9h
pod/dummy-upi-app-56bdd4dcc4-s8pjx   1/1     Running   1             2d9h

NAME                        TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)
service/dummy-upi-service   ClusterIP   10.96.205.5   <none>        3000/TCP

NAME                            READY   UP-TO-DATE   AVAILABLE
deployment.apps/dummy-upi-app   2/2     2            2
```

This confirms that the application is running correctly in Kubernetes and is being tracked by Argo CD.

---

## Step 10: Validate GitOps Self-Healing

To test Argo CD self-healing, the live Kubernetes deployment was manually changed from 2 replicas to 1 replica.

```bash
kubectl get deployment dummy-upi-app -n devsecops

kubectl scale deployment dummy-upi-app --replicas=1 -n devsecops

kubectl get deployment dummy-upi-app -n devsecops
```

Temporary result:

```text
NAME            READY   UP-TO-DATE   AVAILABLE
dummy-upi-app   1/1     1            1
```

Because GitHub defines the desired replica count as 2, Argo CD detected the drift and automatically restored the deployment back to 2 replicas.

Verification:

```bash
kubectl get application dummy-upi-app -n argocd

kubectl get deployment dummy-upi-app -n devsecops

kubectl get pods -n devsecops
```

Verified result:

```text
NAME            SYNC STATUS   HEALTH STATUS
dummy-upi-app   Synced        Healthy

NAME            READY   UP-TO-DATE   AVAILABLE
dummy-upi-app   2/2     2            2
```

Running pods after self-healing:

```text
dummy-upi-app-56bdd4dcc4-8vvmf   1/1 Running
dummy-upi-app-56bdd4dcc4-crzfr   1/1 Running
```

This proves that Argo CD self-healing is working correctly.

---

## Final GitOps Flow

```text
Developer pushes Kubernetes manifests to GitHub
↓
GitHub repository acts as source of truth
↓
Argo CD watches the repository
↓
Argo CD reads k8s/base manifests
↓
Argo CD syncs manifests to Kubernetes
↓
Kubernetes runs dummy UPI application
↓
Manual drift is detected
↓
Argo CD self-heals cluster state
```

---

## Evidence Collected

| Evidence | Result |
|---|---|
| Argo CD namespace | Created |
| Argo CD pods | Running |
| Argo CD server | Running |
| Argo CD repo server | Running |
| Argo CD application controller | Running |
| Argo CD application | dummy-upi-app |
| Git repository source | Configured |
| Manifest path | k8s/base |
| Sync status | Synced |
| Health status | Healthy |
| Automated sync | Enabled |
| Prune | Enabled |
| Self-heal | Enabled |
| Kubernetes deployment | 2/2 available |
| Kubernetes service | ClusterIP |
| Self-healing test | Passed |
| Git commit | 5532924 |

---

## Security and DevOps Value Added

This phase adds the following value:

* GitHub becomes the single source of truth for Kubernetes manifests
* Manual cluster changes are automatically corrected
* Kubernetes deployments become declarative and auditable
* Argo CD provides visibility into sync and health status
* Self-healing reduces configuration drift
* Automated sync improves release consistency
* Prune support removes resources deleted from Git
* GitOps prepares the project for production-style Kubernetes delivery
* Provides a strong foundation for monitoring, runtime security, and autonomous remediation
