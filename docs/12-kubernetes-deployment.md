# Phase 9: Kubernetes Deployment

## Objective

The objective of this phase is to deploy the dummy UPI application to a local Kubernetes cluster.

This phase moves the application from local Docker container execution toward a cloud-native deployment model using Kubernetes manifests.

The Kubernetes deployment validates:

* Local Kubernetes cluster setup
* Namespace-based workload isolation
* Application Deployment resource
* ClusterIP Service exposure
* Replica-based availability
* Health endpoint validation
* Kubernetes readiness and liveness probes
* Application access using port-forwarding

---

## Tool Used

| Tool / Component | Purpose |
|---|---|
| kind | Local Kubernetes cluster running inside Docker |
| kubectl | Kubernetes command-line management |
| Docker | Builds the dummy UPI application image |
| Kubernetes Namespace | Isolates project workloads |
| Kubernetes Deployment | Runs application pods |
| Kubernetes Service | Provides stable internal access to pods |
| Readiness Probe | Checks if the application is ready to receive traffic |
| Liveness Probe | Checks if the application is healthy and should continue running |
| Kustomize | Applies Kubernetes manifests as a grouped base configuration |

---

## Prerequisites

Before starting this phase, the following phases must be completed:

| Phase | Requirement | Status |
|---|---|---|
| Phase 1 | Environment setup | Completed |
| Phase 2 | Jenkins CI/CD foundation | Completed |
| Phase 3 | SonarQube SAST integration | Completed |
| Phase 4 | Trivy vulnerability scanning | Completed |
| Phase 5 | OWASP ZAP DAST integration | Completed |
| Phase 6 | DefectDojo vulnerability management | Completed |
| Phase 7 | SBOM and Cosign supply chain security | Completed |
| Phase 8 | AI Security Intelligence Layer | Completed |

Required tools:

```text
Docker
kubectl
kind
```

---

## Step 1: Kubernetes Client Verification

The Kubernetes client was verified using:

```bash
kubectl version --client
```

Verified result:

```text
Client Version: v1.36.1
Kustomize Version: v5.8.1
```

Initially, no Kubernetes context was configured in WSL.

Observed issue:

```text
error: current-context is not set
```

This confirmed that `kubectl` was installed, but no Kubernetes cluster was configured.

---

## Step 2: Local Kubernetes Cluster Setup Using kind

A local Kubernetes cluster was created using kind.

kind was selected because it provides a lightweight Kubernetes cluster inside Docker and works well inside WSL.

Cluster name:

```text
devsecops-cluster
```

Command used:

```bash
kind create cluster --name devsecops-cluster
```

Cluster verification:

```bash
kind version
kubectl get nodes
kubectl get pods -A
```

Verified result:

```text
kind v0.24.0 go1.22.6 linux/amd64

NAME                              STATUS   ROLES           AGE    VERSION
devsecops-cluster-control-plane   Ready    control-plane   113s   v1.31.0
```

System pods verification:

```text
kube-system          coredns                                      Running
kube-system          etcd-devsecops-cluster-control-plane          Running
kube-system          kindnet                                      Running
kube-system          kube-apiserver-devsecops-cluster-control-plane Running
kube-system          kube-controller-manager                       Running
kube-system          kube-proxy                                   Running
kube-system          kube-scheduler                               Running
local-path-storage   local-path-provisioner                       Running
```

---

## Step 3: Kubernetes Manifest Directory Structure

Kubernetes manifests were created under the `k8s/base` directory.

```bash
mkdir -p k8s/base
```

Final structure:

```text
k8s/
└── base/
    ├── deployment.yaml
    ├── kustomization.yaml
    ├── namespace.yaml
    └── service.yaml
```

---

## Step 4: Namespace Manifest

File created:

```text
k8s/base/namespace.yaml
```

Content:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: devsecops
  labels:
    app.kubernetes.io/name: autonomous-devsecops-engine
    app.kubernetes.io/part-of: phase-9-kubernetes-deployment
```

Purpose:

```text
Creates a dedicated Kubernetes namespace for project workloads.
```

---

## Step 5: Deployment Manifest

File created:

```text
k8s/base/deployment.yaml
```

Content:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dummy-upi-app
  namespace: devsecops
  labels:
    app: dummy-upi-app
    app.kubernetes.io/name: dummy-upi-app
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: autonomous-devsecops-engine
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dummy-upi-app
  template:
    metadata:
      labels:
        app: dummy-upi-app
        app.kubernetes.io/name: dummy-upi-app
        app.kubernetes.io/component: backend
        app.kubernetes.io/part-of: autonomous-devsecops-engine
    spec:
      containers:
        - name: dummy-upi-app
          image: dummy-upi-app:k8s-health-v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 3000
              name: http
          readinessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 20
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
```

Key configuration:

| Setting | Value |
|---|---|
| Replicas | 2 |
| Image | dummy-upi-app:k8s-health-v1 |
| Port | 3000 |
| Readiness Probe | `/health` |
| Liveness Probe | `/health` |
| Privilege Escalation | Disabled |
| Linux Capabilities | Dropped |
| Resource Requests | CPU 100m, Memory 128Mi |
| Resource Limits | CPU 500m, Memory 512Mi |

---

## Step 6: Service Manifest

File created:

```text
k8s/base/service.yaml
```

Content:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: dummy-upi-service
  namespace: devsecops
  labels:
    app: dummy-upi-app
    app.kubernetes.io/name: dummy-upi-service
    app.kubernetes.io/component: service
    app.kubernetes.io/part-of: autonomous-devsecops-engine
spec:
  type: ClusterIP
  selector:
    app: dummy-upi-app
  ports:
    - name: http
      port: 3000
      targetPort: 3000
```

Purpose:

```text
Creates a stable internal Kubernetes service for the dummy UPI application pods.
```

---

## Step 7: Kustomization Manifest

File created:

```text
k8s/base/kustomization.yaml
```

Content:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
```

Purpose:

```text
Allows all Kubernetes manifests to be applied together using kubectl apply -k.
```

---

## Step 8: Manifest Validation

The Kubernetes manifests were validated using dry-run mode.

Command:

```bash
kubectl apply --dry-run=client -k k8s/base
```

Verified result:

```text
namespace/devsecops created (dry run)
service/dummy-upi-service created (dry run)
deployment.apps/dummy-upi-app created (dry run)
```

After updating the deployment later, dry-run result showed:

```text
namespace/devsecops unchanged (dry run)
service/dummy-upi-service unchanged (dry run)
deployment.apps/dummy-upi-app configured (dry run)
```

---

## Step 9: Add Kubernetes Health Endpoint

The application originally responded successfully on `/`, but `/health` was not available.

Initial test result:

```text
UPI Mock Gateway is Online. Awaiting transactions...

Cannot GET /health
```

A Kubernetes health endpoint was added to:

```text
dummy-upi-app/server.js
```

Added route:

```javascript
// Endpoint 1.1: Kubernetes Health Check
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'dummy-upi-app',
    message: 'UPI Mock Gateway health check passed'
  });
});
```

Purpose:

```text
Supports Kubernetes readiness and liveness probes.
```

---

## Step 10: Build Docker Image for Kubernetes

The updated Docker image was built locally.

Command:

```bash
docker build -t dummy-upi-app:k8s-health-v1 ./dummy-upi-app
```

Because kind runs Kubernetes nodes as Docker containers, the image was loaded into the kind cluster.

Command:

```bash
kind load docker-image dummy-upi-app:k8s-health-v1 --name devsecops-cluster
```

---

## Step 11: Deploy Application to Kubernetes

The Kubernetes manifests were applied.

Command:

```bash
kubectl apply -k k8s/base
```

Verified result:

```text
namespace/devsecops unchanged
service/dummy-upi-service unchanged
deployment.apps/dummy-upi-app configured
```

The deployment rollout was verified.

Command:

```bash
kubectl rollout status deployment/dummy-upi-app -n devsecops
```

Verified result:

```text
deployment "dummy-upi-app" successfully rolled out
```

---

## Step 12: Verify Kubernetes Resources

Command:

```bash
kubectl get all -n devsecops
```

Verified result:

```text
NAME                                READY   STATUS    RESTARTS   AGE
pod/dummy-upi-app-c5cbb998b-5bvvh   1/1     Running   0          114s
pod/dummy-upi-app-c5cbb998b-xhmcq   1/1     Running   0          114s

NAME                        TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
service/dummy-upi-service   ClusterIP   10.96.205.5   <none>        3000/TCP   114s

NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/dummy-upi-app   2/2     2            2           114s

NAME                                      DESIRED   CURRENT   READY   AGE
replicaset.apps/dummy-upi-app-c5cbb998b   2         2         2       114s
```

After health probe update, new pods were rolled out:

```text
NAME                             READY   STATUS    RESTARTS   AGE
dummy-upi-app-56bdd4dcc4-8vvmf   1/1     Running   0          11s
dummy-upi-app-56bdd4dcc4-s8pjx   1/1     Running   0          21s
```

---

## Step 13: Verify Readiness Probe

Command:

```bash
kubectl describe deployment dummy-upi-app -n devsecops | grep -A20 -i "readiness"
```

Verified result:

```text
Readiness: http-get http://:3000/health delay=5s timeout=1s period=10s #success=1 #failure=3
```

This confirms Kubernetes readiness probe is configured successfully.

---

## Step 14: Access Application Using Port Forward

The ClusterIP service was exposed locally using port-forwarding.

Command:

```bash
kubectl port-forward svc/dummy-upi-service 3000:3000 -n devsecops
```

The application was tested from another WSL terminal.

Command:

```bash
curl http://localhost:3000

curl http://localhost:3000/health
```

Verified output:

```text
UPI Mock Gateway is Online. Awaiting transactions...
```

Health endpoint output:

```json
{
  "status": "UP",
  "service": "dummy-upi-app",
  "message": "UPI Mock Gateway health check passed"
}
```

---

## Step 15: Git Commit

The Kubernetes deployment work was committed and pushed to GitHub.

Command:

```bash
git add dummy-upi-app/server.js k8s/base

git commit -m "feat: deploy dummy UPI app to Kubernetes"

git push origin main
```

Verified commit:

```text
ad2823c feat: deploy dummy UPI app to Kubernetes
```

Files added or updated:

```text
dummy-upi-app/server.js
k8s/base/deployment.yaml
k8s/base/kustomization.yaml
k8s/base/namespace.yaml
k8s/base/service.yaml
```

---

## Final Kubernetes Deployment Flow

```text
Docker Build
↓
Load Image into kind Cluster
↓
Apply Kubernetes Manifests
↓
Create Namespace
↓
Create Deployment
↓
Create Service
↓
Start 2 Application Pods
↓
Validate Readiness and Liveness Health Check
↓
Access Application using Port Forward
```

---

## Evidence Collected

| Evidence | Result |
|---|---|
| kind cluster | Running |
| Kubernetes node | Ready |
| Namespace | devsecops |
| Deployment | dummy-upi-app |
| Replicas | 2/2 |
| Pods | Running |
| Service | dummy-upi-service |
| Service Type | ClusterIP |
| Application root endpoint | Working |
| Application health endpoint | Working |
| Readiness probe | Configured |
| Liveness probe | Configured |
| Git commit | ad2823c |

---

## Security Value Added

This phase adds the following security and platform value:

* Moves the application toward cloud-native deployment
* Uses namespace-level workload isolation
* Runs multiple replicas for availability
* Adds Kubernetes readiness and liveness health checks
* Applies container security context controls
* Disables privilege escalation
* Drops Linux capabilities
* Defines CPU and memory requests and limits
* Uses declarative Kubernetes manifests
* Prepares the project for GitOps deployment with Argo CD
* Creates a foundation for monitoring, runtime security, and self-healing
