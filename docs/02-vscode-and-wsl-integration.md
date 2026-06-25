# Phase 1: VS Code and WSL Integration

## Objective
Configure Visual Studio Code to act as the primary IDE, seamlessly bridging the Windows UI with the Ubuntu WSL2 backend file system and terminal.

## Step-by-Step Setup

**1. Install Visual Studio Code**
Download and install VS Code on your Windows 11 host from [code.visualstudio.com](https://code.visualstudio.com/).

**2. Install the WSL Extension**
* Open VS Code.
* Navigate to the **Extensions** tab (`Ctrl+Shift+X`).
* Search for **"WSL"** (Publisher: Microsoft) and install it.

**3. Initialize the Project Directory**
Open your Ubuntu terminal and create the DevSecOps project folder:

```bash
mkdir -p ~/projects/Autonomous-DevSecOps-Engine/autonomous-devsecops-engine
cd ~/projects/Autonomous-DevSecOps-Engine/autonomous-devsecops-engine
```

**4. Launch VS Code in WSL Context**
From inside the Ubuntu terminal, open the current directory in VS Code:
```bash
code .
```

**5. Verification**

Look at the bottom-left corner of the VS Code window. It should display a blue badge reading "WSL: Ubuntu-24.04".

Open the integrated terminal (Ctrl+ ` ). It should automatically open a Linux bash shell, not Windows PowerShell.
