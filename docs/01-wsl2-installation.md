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
