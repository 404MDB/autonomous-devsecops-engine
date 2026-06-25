# Phase 2: Jenkins Deployment & DooD Architecture

## Objective
Deploy a Jenkins CI/CD server. To allow Jenkins to trigger security scanning tools (like SonarQube or Trivy) in separate containers, we implement a **Docker-out-of-Docker (DooD)** architecture.

## Step-by-Step Deployment

**1. Create the Custom Jenkins Dockerfile**
Standard Jenkins images lack the Docker CLI. We must build a custom image.
Create a directory and Dockerfile:
```bash
mkdir -p docker/jenkins && cd docker/jenkins
nano Dockerfile
```
Paste the following content:
```bash
FROM jenkins/jenkins:lts-jdk17
USER root
# Install Docker CLI
RUN apt-get update && apt-get install -y docker.io
USER jenkins
```

**2. Build the Custom Image:**
```bash
docker build -t custom-jenkins-docker .
```

**3. Run the Jenkins Container (DooD Mapping)**
Run the container, critically mounting the host's docker.sock to the container's docker.sock:
```bash
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  custom-jenkins-docker
```

**4. Initial Jenkins Setup:**
Retrieve the initial administrator password:
```bash
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
-Navigate to http://localhost:8080 in your Windows browser.
-Paste the password.
-Select Install suggested plugins and create your admin user account.

**5. Verify Docker Access Inside Jenkins:**
Ensure Jenkins has permission to talk to the host's Docker engine:
```bash
docker exec -it jenkins docker ps
```
