# Phase 11: Monitoring and Observability

## Objective

The objective of this phase is to implement Kubernetes monitoring and observability using Prometheus, Grafana, Alertmanager, and Prometheus Operator.

This phase validates:

* Kubernetes cluster monitoring
* Prometheus metrics collection
* Grafana dashboard access
* Alertmanager readiness
* Application-level metrics for the dummy UPI application
* Prometheus ServiceMonitor integration
* PrometheusRule-based alerting
* GitOps-compatible monitoring configuration

---

## Tool Used

| Tool / Component | Purpose |
|---|---|
| Helm | Package manager for Kubernetes |
| kube-prometheus-stack | Monitoring stack installation |
| Prometheus | Metrics collection and querying |
| Grafana | Metrics visualization and dashboards |
| Alertmanager | Alert routing and alert management |
| Prometheus Operator | Manages Prometheus custom resources |
| kube-state-metrics | Exposes Kubernetes object metrics |
| node-exporter | Exposes node-level metrics |
| ServiceMonitor | Defines application scrape target |
| PrometheusRule | Defines application alert rules |

---

## Prerequisites

Before starting this phase, the following phases must be completed:

| Phase | Requirement | Status |
|---|---|---|
| Phase 9 | Kubernetes Deployment | Completed |
| Phase 10 | GitOps with Argo CD | Completed |

The Kubernetes application must already be running:

```text
Namespace: devsecops
Deployment: dummy-upi-app
Service: dummy-upi-service
Replicas: 2
```

---

## Step 1: Verify Kubernetes Cluster

```bash
kubectl get nodes
```

Verified result:

```text
NAME                              STATUS   ROLES           VERSION
devsecops-cluster-control-plane   Ready    control-plane   v1.31.0
```

---

## Step 2: Install Helm

Helm was required to install the monitoring stack.

```bash
helm version --short
```

Verified result:

```text
v3.21.3+g1ad6e68
```

---

## Step 3: Add Prometheus Community Helm Repository

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm repo update

helm search repo prometheus-community/kube-prometheus-stack | head
```

Verified result:

```text
NAME                                           CHART VERSION   APP VERSION
prometheus-community/kube-prometheus-stack     88.1.2          v0.93.0
```

---

## Step 4: Create Monitoring Values File

A custom Helm values file was created.

File:

```text
k8s/monitoring/values.yaml
```

Content:

```yaml
grafana:
  enabled: true
  service:
    type: ClusterIP
  adminUser: admin
  defaultDashboardsEnabled: true

prometheus:
  enabled: true
  service:
    type: ClusterIP
  prometheusSpec:
    retention: 2d
    retentionSize: 1GB

alertmanager:
  enabled: true
  service:
    type: ClusterIP

kubeStateMetrics:
  enabled: true

nodeExporter:
  enabled: true

prometheusOperator:
  enabled: true
```

---

## Step 5: Install kube-prometheus-stack

The monitoring namespace was created and the monitoring stack was installed using Helm.

```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  -f k8s/monitoring/values.yaml \
  --wait \
  --timeout 15m
```

Verified result:

```text
namespace/monitoring created

NAME: monitoring
NAMESPACE: monitoring
STATUS: deployed
REVISION: 1
```

---

## Step 6: Verify Monitoring Pods

```bash
kubectl get pods -n monitoring
```

Verified result:

```text
alertmanager-monitoring-kube-prometheus-alertmanager-0   2/2 Running
monitoring-grafana                                      3/3 Running
monitoring-kube-prometheus-operator                     1/1 Running
monitoring-kube-state-metrics                           1/1 Running
monitoring-prometheus-node-exporter                     1/1 Running
prometheus-monitoring-kube-prometheus-prometheus-0      2/2 Running
```

---

## Step 7: Verify Monitoring Services

```bash
kubectl get svc -n monitoring
```

Verified important services:

```text
monitoring-grafana
monitoring-kube-prometheus-alertmanager
monitoring-kube-prometheus-operator
monitoring-kube-prometheus-prometheus
monitoring-kube-state-metrics
monitoring-prometheus-node-exporter
```

---

## Step 8: Verify Prometheus and Alertmanager Resources

```bash
kubectl get prometheus -n monitoring

kubectl get alertmanager -n monitoring
```

Verified result:

```text
Prometheus:
monitoring-kube-prometheus-prometheus
READY: 1
RECONCILED: True
AVAILABLE: True

Alertmanager:
monitoring-kube-prometheus-alertmanager
READY: 1
RECONCILED: True
AVAILABLE: True
```

---

## Step 9: Access Grafana, Prometheus, and Alertmanager

The monitoring UIs were accessed using local port-forwarding.

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80

kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090

kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

Access URLs:

```text
Grafana:      http://localhost:3001
Prometheus:   http://localhost:9090
Alertmanager: http://localhost:9093
```

Grafana password command:

```bash
kubectl get secret --namespace monitoring monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d; echo
```

Readiness checks:

```bash
curl -s http://localhost:9090/-/ready

curl -s http://localhost:9093/-/ready

curl -s http://localhost:3001/api/health
```

Verified result:

```text
Prometheus Server is Ready.
OK
Grafana database: ok
```

---

## Step 10: Add Application Metrics Endpoint

The dummy UPI application was updated to expose Prometheus metrics using `prom-client`.

Package installed:

```bash
npm --prefix dummy-upi-app install prom-client --save
```

File updated:

```text
dummy-upi-app/server.js
```

Metrics endpoint added:

```text
/metrics
```

Custom metric added:

```text
dummy_upi_http_requests_total
```

Local Docker test:

```bash
docker build -t dummy-upi-app:metrics-v1 ./dummy-upi-app

docker run -d --rm \
  --name dummy-upi-metrics-test \
  -p 3005:3000 \
  dummy-upi-app:metrics-v1

curl http://localhost:3005/health

curl http://localhost:3005/metrics | head -30

docker stop dummy-upi-metrics-test
```

Verified metrics:

```text
process_resident_memory_bytes
dummy_upi_http_requests_total
```

---

## Step 11: Load Metrics Image into kind

```bash
docker build -t dummy-upi-app:metrics-v1 ./dummy-upi-app

kind load docker-image dummy-upi-app:metrics-v1 --name devsecops-cluster
```

The Kubernetes deployment image was updated:

```text
dummy-upi-app:metrics-v1
```

File updated:

```text
k8s/base/deployment.yaml
```

Verified result:

```bash
kubectl get deployment dummy-upi-app -n devsecops \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

Output:

```text
dummy-upi-app:metrics-v1
```

---

## Step 12: Verify GitOps Sync Through Argo CD

After pushing the manifest update to GitHub, Argo CD synchronized the new application image.

```bash
kubectl get application dummy-upi-app -n argocd

kubectl get pods -n devsecops \
  -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,STATUS:.status.phase
```

Verified result:

```text
dummy-upi-app   Synced   Healthy

dummy-upi-app-d9c566c9d-dklfr   dummy-upi-app:metrics-v1   Running
dummy-upi-app-d9c566c9d-scml2   dummy-upi-app:metrics-v1   Running
```

---

## Step 13: Create ServiceMonitor for Application Metrics

A ServiceMonitor was created so Prometheus can scrape the dummy UPI application.

File:

```text
k8s/monitoring/dummy-upi-servicemonitor.yaml
```

Content:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dummy-upi-app
  namespace: monitoring
  labels:
    release: monitoring
    app.kubernetes.io/name: dummy-upi-app
    app.kubernetes.io/part-of: autonomous-devsecops-engine
    app.kubernetes.io/component: monitoring
spec:
  namespaceSelector:
    matchNames:
      - devsecops
  selector:
    matchLabels:
      app: dummy-upi-app
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
      scrapeTimeout: 10s
```

Applied using:

```bash
kubectl apply -f k8s/monitoring/dummy-upi-servicemonitor.yaml
```

Verified result:

```text
servicemonitor.monitoring.coreos.com/dummy-upi-app configured
```

---

## Step 14: Verify Application Metrics from Kubernetes

The application was accessed through port-forwarding.

```bash
kubectl port-forward -n devsecops deployment/dummy-upi-app 3010:3000
```

Health endpoint:

```bash
curl -s http://localhost:3010/health
```

Verified result:

```json
{
  "status": "UP",
  "service": "dummy-upi-app",
  "message": "UPI Mock Gateway health check passed"
}
```

Metrics endpoint:

```bash
curl -s http://localhost:3010/metrics | grep -E "dummy_upi_http_requests_total|process_resident_memory_bytes" | head -20
```

Verified result:

```text
process_resident_memory_bytes
dummy_upi_http_requests_total{method="GET",route="/health",status_code="200"}
dummy_upi_http_requests_total{method="GET",route="/metrics",status_code="200"}
```

---

## Step 15: Verify Prometheus Scraping

Prometheus was queried directly through its API.

```bash
curl -G -s "http://localhost:9090/api/v1/query" \
  --data-urlencode 'query=up{namespace="devsecops",job="dummy-upi-service"}' | python3 -m json.tool
```

Verified result:

```text
dummy-upi-app pod 1: up = 1
dummy-upi-app pod 2: up = 1
```

Custom application metric query:

```bash
curl -G -s "http://localhost:9090/api/v1/query" \
  --data-urlencode 'query=dummy_upi_http_requests_total' | python3 -m json.tool
```

Verified result:

```text
dummy_upi_http_requests_total metric visible for both pods
Routes monitored:
- /health
- /metrics
Status code:
- 200
```

---

## Step 16: Add Prometheus Alert Rules

A PrometheusRule was created for application alerting.

File:

```text
k8s/monitoring/dummy-upi-prometheusrule.yaml
```

Alerts added:

```text
DummyUPIAppDown
DummyUPIHighHttp5xxErrors
```

Rule summary:

```text
DummyUPIAppDown:
Triggers when Prometheus cannot scrape dummy-upi-service for more than 1 minute.

DummyUPIHighHttp5xxErrors:
Triggers when the dummy UPI application returns HTTP 5xx errors.
```

Applied using:

```bash
kubectl apply -f k8s/monitoring/dummy-upi-prometheusrule.yaml
```

Verified result:

```bash
kubectl get prometheusrule dummy-upi-app-alerts -n monitoring
```

Output:

```text
NAME                   AGE
dummy-upi-app-alerts   Running
```

---

## Step 17: Verify Alert Rule Evaluation

Prometheus alert rules were exported and checked.

```bash
curl -G -s "http://localhost:9090/api/v1/rules" \
  --data-urlencode 'type=alert' \
  -o reports/phase-11-monitoring/prometheus-alert-rules.json
```

Alert rule verification:

```text
Rule Group: dummy-upi-app.rules
Alert: DummyUPIAppDown
State: inactive
Health: ok

Alert: DummyUPIHighHttp5xxErrors
State: inactive
Health: ok
```

`inactive` is the expected healthy state because the dummy UPI application is running and Prometheus is scraping it successfully.

---

## Evidence Collected

| Evidence | Result |
|---|---|
| Helm installed | v3.21.3 |
| kube-prometheus-stack chart | 88.1.2 |
| Monitoring namespace | Created |
| Helm release | monitoring deployed |
| Grafana pod | Running |
| Prometheus pod | Running |
| Alertmanager pod | Running |
| Prometheus Operator | Running |
| kube-state-metrics | Running |
| node-exporter | Running |
| Grafana API | Healthy |
| Prometheus API | Ready |
| Alertmanager API | Ready |
| Application image | dummy-upi-app:metrics-v1 |
| Application health endpoint | Working |
| Application metrics endpoint | Working |
| ServiceMonitor | Created |
| Prometheus scrape status | up = 1 |
| Custom metric | dummy_upi_http_requests_total |
| PrometheusRule | Created |
| Alert rule health | ok |
| Alert state | inactive |

---

## Security and DevOps Value Added

This phase adds the following value:

* Provides visibility into Kubernetes cluster health
* Enables monitoring of application availability
* Adds Prometheus-based application metrics
* Tracks HTTP request activity for the dummy UPI service
* Enables alerting for application downtime
* Enables alerting for HTTP 5xx error behavior
* Adds Grafana dashboard access for operational visibility
* Adds Alertmanager for future notification routing
* Supports GitOps-compatible observability configuration
* Prepares the project for runtime security monitoring and self-healing automation
