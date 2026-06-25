# Phase 1: Docker Desktop Setup & Integration

## Objective
Install the Docker engine and integrate it with WSL2 to allow seamless container management and Docker-out-of-Docker (DooD) execution directly from the Ubuntu terminal.

## Step-by-Step Installation

**1. Install Docker Desktop for Windows**
Download and install Docker Desktop from the [official website](https://www.docker.com/products/docker-desktop/).

**2. Configure WSL Integration**
* Open Docker Desktop.
* Click the **⚙️ Settings** (gear icon) in the top right.
* Navigate to **General** and ensure **"Use the WSL 2 based engine"** is checked.
* Navigate to **Resources** -> **WSL Integration**.
* Check the box for **"Enable integration with my default WSL distro"** AND toggle the switch specifically for **`Ubuntu-24.04`**.
* Click **Apply & restart** at the bottom right.

**3. Verification**
Open your Ubuntu terminal (via VS Code or standalone) and verify the Docker CLI can communicate with the Docker Daemon running on Windows:
```bash
docker --version
```
# Expected: Docker version 26.1.x (or newer)

docker run hello-world

**Expected Result: A success message stating "Hello from Docker! This message shows that your installation appears to be working correctly."**

