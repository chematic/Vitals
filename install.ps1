$ErrorActionPreference = "Stop"

$installPath = "$env:ProgramFiles\Vitals"
$binPath = "$installPath\bin"
$corePath = "$installPath\core"
$logPath = "$installPath\logs"
$shortcutDir = "$env:AppData\Microsoft\Windows\Start Menu\Programs\Vitals"

if (-not (Test-Path $installPath)) { New-Item -ItemType Directory -Path $installPath | Out-Null }
if (-not (Test-Path $binPath)) { New-Item -ItemType Directory -Path $binPath | Out-Null }
if (-not (Test-Path $logPath)) { New-Item -ItemType Directory -Path $logPath | Out-Null }

$repoUrl = "https://raw.githubusercontent.com/chematic/Vitals/main"

Write-Host "Exporting files..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$repoUrl/main.py" -OutFile "$installPath\main.py"
Invoke-WebRequest -Uri "$repoUrl/requirements.txt" -OutFile "$installPath\requirements.txt"
Invoke-WebRequest -Uri "$repoUrl/start.bat" -OutFile "$installPath\start.bat"

$folders = @("core", "core/providers")
foreach ($folder in $folders) {
    $target = "$installPath\$folder"
    if (-not (Test-Path $target)) { New-Item -ItemType Directory -Path $target | Out-Null }
}

$coreFiles = @("engine.py", "logger.py")
foreach ($file in $coreFiles) {
    Invoke-WebRequest -Uri "$repoUrl/core/$file" -OutFile "$corePath\$file"
}

$providerFiles = @("c.py", "g.py", "m.py", "s.py")
foreach ($file in $providerFiles) {
    Invoke-WebRequest -Uri "$repoUrl/core/providers/$file" -OutFile "$corePath\providers\$file"
}

Write-Host "Exporting binaries..." -ForegroundColor Cyan
$binFiles = @(
    "LibreHardwareMonitorLib.dll",
    "System.Buffers.dll",
    "System.Memory.dll",
    "System.Runtime.CompilerServices.Unsafe.dll"
)

foreach ($dll in $binFiles) {
    Invoke-WebRequest -Uri "$repoUrl/bin/$dll" -OutFile "$binPath\$dll"
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python missing." -ForegroundColor Red
    $choice = Read-Host "Install Python 3.10? (Y/N)"
    if ($choice -eq "Y") {
        Write-Host "Installing Python..." -ForegroundColor Cyan
        winget install -e --id Python.Python.3.10 --silent --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        exit
    }
}

Write-Host "Installing packages..." -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet
python -m pip install keyboard psutil rich py-cpuinfo GPUtil pythonnet --upgrade --quiet

Write-Host "Creating shortcut..." -ForegroundColor Cyan
if (-not (Test-Path $shortcutDir)) { New-Item -ItemType Directory -Path $shortcutDir | Out-Null }
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$shortcutDir\Vitals.lnk")
$Shortcut.TargetPath = "$installPath\start.bat"
$Shortcut.WorkingDirectory = $installPath
$Shortcut.IconLocation = "shell32.dll, 12"
$Shortcut.Save()

Write-Host "Done." -ForegroundColor Green