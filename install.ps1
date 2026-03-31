$ErrorActionPreference = "Stop"

$vitalsProc = Get-Process "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
if ($vitalsProc) {
    Write-Host "Closing Vitals for update..." -ForegroundColor Yellow
    $vitalsProc | Stop-Process -Force
    Start-Sleep -Seconds 1
}

function Show-Spinner {
    param([string]$Message, [scriptblock]$Task)
    $spinner = @('|', '/', '-', '\')
    $i = 0
    $job = Start-Job -ScriptBlock $Task
    while ($job.State -eq 'Running') {
        Write-Host "`r$Message $($spinner[$i % 4])" -NoNewline -ForegroundColor Cyan
        $i++
        Start-Sleep -Milliseconds 100
    }
    $result = Receive-Job -Job $job
    Remove-Job -Job $job
    Write-Host "`r$Message > OK" -ForegroundColor Green
    return $result
}

$installPath = "$env:ProgramFiles\Vitals"
$binPath = "$installPath\bin"
$corePath = "$installPath\core"
$logPath = "$installPath\logs"
$shortcutDir = "$env:AppData\Microsoft\Windows\Start Menu\Programs\Vitals"

Write-Host "Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path $installPath)) { New-Item -ItemType Directory -Path $installPath | Out-Null }
if (-not (Test-Path $binPath)) { New-Item -ItemType Directory -Path $binPath | Out-Null }
if (-not (Test-Path $logPath)) { New-Item -ItemType Directory -Path $logPath | Out-Null }

$repoUrl = "https://raw.githubusercontent.com/chematic/Vitals/main"

Show-Spinner "Fetching root files..." {
    Invoke-WebRequest -Uri "$using:repoUrl/main.py" -OutFile "$using:installPath\main.py"
    Invoke-WebRequest -Uri "$using:repoUrl/requirements.txt" -OutFile "$using:installPath\requirements.txt"
    Invoke-WebRequest -Uri "$using:repoUrl/start.bat" -OutFile "$using:installPath\start.bat"
    Invoke-WebRequest -Uri "$using:repoUrl/install.ps1" -OutFile "$using:installPath\install.ps1"
}

Show-Spinner "Fetching core engine..." {
    $folders = @("core", "core/providers")
    foreach ($folder in $folders) {
        $target = "$using:installPath\$folder"
        if (-not (Test-Path $target)) { New-Item -ItemType Directory -Path $target | Out-Null }
    }
    Invoke-WebRequest -Uri "$using:repoUrl/core/engine.py" -OutFile "$using:corePath\engine.py"
    Invoke-WebRequest -Uri "$using:repoUrl/core/logger.py" -OutFile "$using:corePath\logger.py"
    $providers = @("c.py", "g.py", "m.py", "s.py")
    foreach ($p in $providers) {
        Invoke-WebRequest -Uri "$using:repoUrl/core/providers/$p" -OutFile "$using:corePath\providers\$p"
    }
}

Show-Spinner "Downloading binary dependencies..." {
    $binFiles = @("LibreHardwareMonitorLib.dll", "System.Buffers.dll", "System.Memory.dll", "System.Runtime.CompilerServices.Unsafe.dll")
    foreach ($dll in $binFiles) {
        Invoke-WebRequest -Uri "$using:repoUrl/bin/$dll" -OutFile "$using:binPath\$dll"
    }
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python missing from PATH." -ForegroundColor Red
    $choice = Read-Host "Install Python 3.10 now? [Y] Yes [N] No"
    if ($choice -eq "Y") {
        Show-Spinner "Installing Python 3.10 via Winget..." {
            winget install -e --id Python.Python.3.10 --silent --accept-package-agreements --accept-source-agreements --override "/quiet InstallAllUsers=1 PrependPath=1"
        }
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host "Installation aborted." -ForegroundColor Red
        exit
    }
} else {
    Write-Host "Checking Python version... > OK" -ForegroundColor Green
}

Show-Spinner "Updating Pip and installing modules..." {
    python -m pip install --upgrade pip --quiet
    python -m pip install keyboard psutil rich py-cpuinfo GPUtil pythonnet requests --upgrade --quiet
}

Show-Spinner "Creating system shortcut..." {
    if (-not (Test-Path $using:shortcutDir)) { New-Item -ItemType Directory -Path $using:shortcutDir | Out-Null }
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$using:shortcutDir\Vitals.lnk")
    $Shortcut.TargetPath = "$using:installPath\start.bat"
    $Shortcut.WorkingDirectory = $using:installPath
    $Shortcut.IconLocation = "shell32.dll, 12"
    $Shortcut.Save()
}

Write-Host "`nsuccess" -NoNewline -ForegroundColor Black -BackgroundColor Green
Write-Host " Vitals was successfully installed!" -ForegroundColor Green
Write-Host "info" -NoNewline -ForegroundColor Black -BackgroundColor Cyan
Write-Host " You can now launch Vitals from your Start Menu." -ForegroundColor Cyan