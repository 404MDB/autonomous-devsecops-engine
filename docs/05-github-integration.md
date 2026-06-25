# Phase 2: GitHub Repository & Jenkins Pipeline Integration

## Objective
Establish a reliable connection between the source control repository (GitHub) and the continuous integration server (Jenkins) to pull the declarative pipeline configuration (`Jenkinsfile`) and run automated security checks on every code update.

## Prerequisites
* A public or private GitHub repository initialized.
* Custom Jenkins Docker container running with standard Git plugins installed.

---

## Step-by-Step Configuration

**1: Initialize Git and Structure Locally**
Before connecting to Jenkins, the local directory was structured and tracked via standard Git commands to ensure clean synchronization:
1. Navigated to the root project directory:
   ```bash
   cd ~/projects/Autonomous-DevSecOps-Engine/autonomous-devsecops-engine
   ```
Initialized the repository, staged all architectural documentation files, committed them, and pushed them to the main upstream branch:
```bash
git init
git add .
git commit -m "docs: initialized project architecture and documentation structure"
git branch -M main
git remote add origin [https://github.com/404MDB/autonomous-devsecops-engine.git](https://github.com/404MDB/autonomous-devsecops-engine.git)
git push -u origin main
```

**2: Create and Configure the Jenkins Job**
-Log into the Jenkins Web UI (http://localhost:8080).

-From the left sidebar, click New Item.

-Enter the item name: Autonomous-DevSecOps-Engine.

-Select Pipeline as the job type and click OK at the bottom of the page.

-In the job configuration interface, scroll down to the Pipeline section.

-Change the Definition dropdown menu from Pipeline script to Pipeline script from SCM.

-Set the SCM dropdown menu to Git.

-Paste the Repository URL:
```
https://github.com/404MDB/autonomous-devsecops-engine.git
```
-Adjust the Branch Specifier from */master to match the current GitHub default: */main.

-Ensure the Script Path is set exactly to Jenkinsfile.

**3. Verification and Validation**
-A manual build trigger (Build Now) confirmed the solution succeeded:

-SCM Phase: Jenkins fetched the complete branch tree into /var/jenkins_home/workspace/Autonomous-DevSecOps-Engine@script/.

-Pipeline Launch: The declarative Jenkinsfile structure was read sequentially.

-Console Outcome: The engine verified basic environmental checks and finalized with a Finished: SUCCESS status.
