# Sports Club Backend — One-Click Launcher (Windows PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File start.ps1
#  or just:  .\start.ps1

$ErrorActionPreference = 'Stop'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Sports Club Backend Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Find Python
$python = $null
foreach ($candidate in @("python3", "python")) {
    try { $null = Get-Command $candidate -ErrorAction Stop; $python = $candidate; break } catch {}
}
if (-not $python) {
    Write-Host "ERROR: Python not found. Please install Python 3.10+." -ForegroundColor Red
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
$pyVer = & $python --version 2>&1
Write-Host "[OK] $pyVer" -ForegroundColor Green

# 2. Check/create venv
$venvDir = Join-Path $PSScriptRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $python -m venv $venvDir
    Write-Host "[OK] venv created" -ForegroundColor Green
}

# 3. Install dependencies
$requirements = Join-Path $PSScriptRoot "python\requirements.txt"
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install -q -r $requirements 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    # Retry without quiet mode to show errors
    & $venvPython -m pip install -r $requirements
}
Write-Host "[OK] Dependencies ready" -ForegroundColor Green

# 4. Start backend (SQLite mode — no MySQL needed)
$env:DB_TYPE = "sqlite"
$pythonDir = Join-Path $PSScriptRoot "python"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting backend with SQLite..." -ForegroundColor Cyan
Write-Host " API docs: http://localhost:8081/docs" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $pythonDir
& $venvPython -m uvicorn app.main:app --app-dir $pythonDir --host 0.0.0.0 --port 8081 --reload --no-proxy-headers
