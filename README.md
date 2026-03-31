# 📊 Vitals PRO

**Vitals** is a high-performance system monitoring solution for Windows environments. Developed in Python and powered by a hybrid engine utilizing `LibreHardwareMonitor`, it provides real-time telemetry for CPU (with advanced AMD SMU support), GPU, Memory, and Storage via a modern Terminal User Interface (TUI).

---

## Key Features

* **Low-Level Access:** Utilizes Ring 0 driver access for precise hardware sensor readings.
* **CPU Telemetry:** Real-time tracking of temperatures, frequencies, voltages, and power consumption (Wattage).
* **Graphics Monitoring:** Comprehensive GPU load, temperature, and VRAM utilization metrics.
* **Memory & Storage:** Dynamic visualization of physical RAM and disk occupancy.
* **Thermal Management:** Detection and reporting of system fan speeds (RPM).
* **Automated Updates:** Integrated version synchronization via remote PowerShell execution.
* **Privilege Management:** Native handling of administrative elevation required for hardware access.

---

## Installation

The deployment is fully automated. Open a **PowerShell terminal as Administrator** and execute the following command:

```powershell
iwr -useb [https://raw.githubusercontent.com/chematic/Vitals/main/install.ps1](https://raw.githubusercontent.com/chematic/Vitals/main/install.ps1) | iex
```

### Deployment Stages:
1. **Environment Check:** Verifies or installs **Python 3.10** via Winget.
2. **Path Configuration:** Automatically updates system environment variables.
3. **Resource Acquisition:** Downloads all source files and binary dependencies (`.dll`).
4. **Dependency Management:** Installs required Python packages (`psutil`, `rich`, `pythonnet`, `requests`).
5. **System Integration:** Generates a dedicated shortcut within the Windows Start Menu.

---

## Usage

Launch the application via the Start Menu shortcut or by running `start.bat` located in the installation directory.

### Operational Hotkeys:
* **`Q`**: Terminate the application safely.
* **`L`**: Open the runtime log file (`vitals_runtime.log`) in the default text editor.
* **`R`**: Trigger a hardware engine reset and module reload.

---

## Update Protocol

Vitals includes a synchronized update system. At each initialization, `main.py` validates the local installation against the remote repository:
* If a modification is detected on the master branch, an update prompt is issued.
* Upon user confirmation, the application initiates a high-priority PowerShell session to refresh all local components.

---

## Project Architecture

```text
C:\Program Files\Vitals\
├── bin/                # Binary dependencies and DLLs
├── core/               # Engine logic and hardware providers
│   ├── providers/      # Component-specific logic (CPU, GPU, etc.)
│   ├── engine.py       # Core hardware interface
│   └── logger.py       # Event tracking system
├── logs/               # Operational logs
├── install.ps1         # Deployment and maintenance script
├── main.py             # Entry point and UI logic
└── start.bat           # Optimized execution script
```

---

## Requirements

* **Operating System:** Windows 10 or 11.
* **Privileges:** Administrative rights are mandatory for hardware sensor synchronization.
