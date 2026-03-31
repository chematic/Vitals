# VITALS

Modular hardware monitoring framework for Windows systems.

## Features
- Isolated Python 3.10 environment (Embedded).
- Low-level CPU, GPU, and RAM telemetry.
- Automated dependency management.
- Admin-privileged execution by default.

## Installation
Run PowerShell as Administrator in the root directory and execute:
Set-ExecutionPolicy Bypass -Scope Process -Force; .\install.ps1

## Usage
Once the installation is complete, use the generated `start.bat` file. 
The engine requires Administrator privileges to access hardware sensors.

## Architecture
- /core: Main logic and data providers.
- /bin: Binary dependencies (.dll).
- /python: Isolated environment (generated on setup).
