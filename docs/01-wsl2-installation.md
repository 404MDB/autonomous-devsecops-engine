# Phase 1: WSL2 and Ubuntu 24.04 Setup

## Objective
Establish a native Linux development environment on a Windows 11 host machine to support containerized DevSecOps tools without the overhead of traditional virtual machines.

## Prerequisites
* Windows 11 Host Machine.
* Hardware Virtualization enabled in BIOS/UEFI.

## Step-by-Step Installation

**1. Enable Windows Subsystem for Linux (WSL)**
Open PowerShell as an **Administrator** and run the following command to install WSL and the default Ubuntu distribution:
```powershell
wsl --install
```
**2. Set Default WSL Version**
Ensure that WSL defaults to version 2 for better performance and full system call compatibility:
```powershell
wsl --set-default-version 2
```
**3. Install Ubuntu 24.04**
If Ubuntu 24.04 wasn't installed by default, install it via the Microsoft Store or by running:
```powershell
wsl --install -d Ubuntu-24.04
```

**4. Initial Linux Setup**
Once the installation finishes, a terminal will open asking you to create a UNIX username and password. After setting this up, update the Linux package manager:
```bash
sudo apt update && sudo apt upgrade -y
```

**5. Verification**
Open a new PowerShell window and confirm the installation:
```bash
wsl -l -v
```

**Expected Output: You should see Ubuntu-24.04 listed with State Running and Version 2**
