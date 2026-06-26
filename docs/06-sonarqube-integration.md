# Phase 3: SAST Implementation with SonarQube

## Objective
Deploy SonarQube to perform Static Application Security Testing (SAST) and configure the Docker-out-of-Docker network bridge to allow Jenkins to push security metrics directly to the SonarQube dashboard.

## Prerequisites
* Phase 1 and Phase 2 completed (Jenkins running with DooD access).
* Minimum of 2GB RAM available for the SonarQube container.

---

## Step-by-Step Configuration

**Step 1: Kernel Memory Configuration (CRITICAL)**
SonarQube relies on an embedded Elasticsearch database to index code metrics. By default, the WSL2 Ubuntu kernel restricts the maximum number of memory map areas (`vm.max_map_count`) to 65,530, which will cause the SonarQube container to crash immediately with an `OutOfMemoryError`.

To resolve this, the limit was increased dynamically on the host:
```bash
sudo sysctl -w vm.max_map_count=262144
```

**Step 2: SonarQube Container Deployment**
SonarQube was deployed using the Community LTS image. Persistent named volumes were attached to ensure security data, user configurations, and plugin extensions survive container restarts.
```bash
docker run -d --name sonarqube \
  -p 9000:9000 \
  -v sonarqube_data:/opt/sonarqube/data \
  -v sonarqube_extensions:/opt/sonarqube/extensions \
  -v sonarqube_logs:/opt/sonarqube/logs \
  sonarqube:lts-community
```

**Step 3: API Token Generation**
To allow Jenkins to securely transmit reports to SonarQube without exposing administrator credentials:
-Logged into SonarQube at http://localhost:9000 (Default: admin/admin).

-Navigated to Administration -> Security -> Users.

-Generated a non-expiring User Token named jenkins-sast-token.

**Step 3: API Token Generation**
To allow Jenkins to securely transmit reports to SonarQube without exposing administrator credentials:

Logged into SonarQube at http://localhost:9000 (Default: admin/admin).

Navigated to Administration -> Security -> Users.

Generated a non-expiring User Token named jenkins-sast-token.

**Step 4: Jenkins Systems Integration**
The API token and server endpoints were integrated into the Jenkins environment.

1. Secret Configuration:

Navigated to Manage Jenkins -> Credentials.

Added a Secret text global credential containing the SonarQube token, assigned with the strict ID: sonarqube-token.

2. Server Definition:

Navigated to Manage Jenkins -> System.

Added a SonarQube Server named exactly SonarQube.

Configured the Server URL to target the Docker bridge gateway: http://172.17.0.1:9000 (This prevents Jenkins from looping back to its own localhost).

Attached the sonarqube-token credential.

3. Tool Installation:

Navigated to Manage Jenkins -> Tools.

Added a SonarQube Scanner installation named exactly SonarScanner, with the "Install automatically" flag checked.

**Step 5: Jenkinsfile Pipeline Update**
The declarative pipeline was updated to include the SCANNER_HOME environment variable and a new SAST execution stage. Documentation and infrastructure directories were explicitly excluded to speed up scan times and prevent false positives.
```bash
stage('SAST: SonarQube Code Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') { 
                    sh """
                    \${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=autonomous-devsecops-engine \
                      -Dsonar.projectName="Autonomous DevSecOps Engine" \
                      -Dsonar.sources=. \
                      -Dsonar.exclusions=reports/**,screenshots/**,docker/**,docs/**
                    """
                }
            }
        }
```
**Verification**
A pipeline build was manually triggered. The console output confirmed:

Jenkins successfully downloaded the sonar-scanner-cli binary.

The scanner successfully communicated with the SonarQube Server at http://172.17.0.1:9000.

The project Autonomous DevSecOps Engine was automatically provisioned in the SonarQube dashboard with a "Passed" quality gate status.
