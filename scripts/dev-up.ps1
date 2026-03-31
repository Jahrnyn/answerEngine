# scripts/dev-up.ps1 — CfHEE-aware draft update

param(
    [int]$BackendPort = 8761,
    [int]$FrontendPort = 8760,
    [string]$CfheeBaseUrl = "http://127.0.0.1:8770"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

$BackendDir = Join-Path $RepoRoot "apps/backend"
$FrontendDir = Join-Path $RepoRoot "apps/frontend"

$BackendVenvDir = Join-Path $BackendDir ".venv"
$BackendPython = Join-Path $BackendVenvDir "Scripts/python.exe"
$BackendPyproject = Join-Path $BackendDir "pyproject.toml"
$BackendDepsMarker = Join-Path $BackendVenvDir ".deps-installed"

$FrontendPackageJson = Join-Path $FrontendDir "package.json"
$FrontendLockFile = Join-Path $FrontendDir "package-lock.json"
$FrontendNodeModules = Join-Path $FrontendDir "node_modules"
$FrontendDepsMarker = Join-Path $FrontendNodeModules ".deps-installed"

$CfheeHealthUrl = "$($CfheeBaseUrl.TrimEnd('/'))/api/v1/health"
$CfheeCapabilitiesUrl = "$($CfheeBaseUrl.TrimEnd('/'))/api/v1/capabilities"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Test-CommandAvailable {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-PythonLauncher {
    if (Test-CommandAvailable "py") {
        return @{
            Path = (Get-Command "py").Source
            Args = @("-3.12")
        }
    }

    if (Test-CommandAvailable "python") {
        return @{
            Path = (Get-Command "python").Source
            Args = @()
        }
    }

    Fail "Python was not found. Install Python 3.12+ and make sure 'py' or 'python' is on PATH."
}

function Update-InstallMarker {
    param([string]$Path)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Set-Content -Path $Path -Value $timestamp
}

function Test-BackendDependenciesInstalled {
    if (-not (Test-Path $BackendPython) -or -not (Test-Path $BackendDepsMarker)) {
        return $false
    }

    if (-not (Test-Path $BackendPyproject)) {
        return $false
    }

    return (Get-Item $BackendDepsMarker).LastWriteTimeUtc -ge (Get-Item $BackendPyproject).LastWriteTimeUtc
}

function Test-FrontendDependenciesInstalled {
    if (-not (Test-Path $FrontendNodeModules) -or -not (Test-Path $FrontendDepsMarker)) {
        return $false
    }

    if (-not (Test-Path $FrontendPackageJson)) {
        return $false
    }

    $markerTime = (Get-Item $FrontendDepsMarker).LastWriteTimeUtc
    if ($markerTime -lt (Get-Item $FrontendPackageJson).LastWriteTimeUtc) {
        return $false
    }

    if (Test-Path $FrontendLockFile) {
        return $markerTime -ge (Get-Item $FrontendLockFile).LastWriteTimeUtc
    }

    return $true
}

function Test-HttpEndpoint {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

function Wait-ForHttpEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-HttpEndpoint -Url $Url) {
            return $true
        }
        Start-Sleep -Seconds 2
    }

    return $false
}

function Start-DevWindow {
    param(
        [string]$Title,
        [string]$WorkingDirectory,
        [string]$Command
    )

    $windowCommand = "`$Host.UI.RawUI.WindowTitle = '$Title'; Set-Location '$WorkingDirectory'; $Command"
    Start-Process -FilePath "powershell.exe" -WorkingDirectory $WorkingDirectory -ArgumentList @("-NoExit", "-Command", $windowCommand) | Out-Null
}

function Get-OllamaBaseUrl {
    if ($env:OLLAMA_BASE_URL) {
        return $env:OLLAMA_BASE_URL.TrimEnd("/")
    }

    return "http://127.0.0.1:11434"
}

function Invoke-OllamaTags {
    param([string]$Url)

    try {
        return Invoke-RestMethod -Uri "$Url/api/tags" -Method Get -TimeoutSec 3
    }
    catch {
        return $null
    }
}

function Get-CfheeJson {
    param([string]$Url)

    try {
        return Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5
    }
    catch {
        return $null
    }
}

function Test-CfheeCapabilities {
    param($CapabilitiesResponse)

    if ($null -eq $CapabilitiesResponse) {
        return $false
    }

    if ($CapabilitiesResponse.service -ne "cfhee") {
        return $false
    }

    if ($CapabilitiesResponse.api_version -ne "v1") {
        return $false
    }

    if ($null -eq $CapabilitiesResponse.capabilities) {
        return $false
    }

    if (-not $CapabilitiesResponse.capabilities.scoped_retrieval) {
        return $false
    }

    if (-not $CapabilitiesResponse.capabilities.scope_values) {
        return $false
    }

    return $true
}

$OllamaBaseUrl = Get-OllamaBaseUrl
$BackendUrl = "http://127.0.0.1:$BackendPort"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$HealthUrl = "$BackendUrl/health"

Write-Step "Checking required tools"

if (-not (Test-CommandAvailable "npm.cmd") -and -not (Test-CommandAvailable "npm")) {
    Fail "npm was not found. Install Node.js and reopen PowerShell."
}

$pythonLauncher = Get-PythonLauncher

Write-Step "Checking repository structure"

if (-not (Test-Path $BackendDir)) {
    Fail "Backend directory '$BackendDir' was not found."
}

if (-not (Test-Path $FrontendDir)) {
    Fail "Frontend directory '$FrontendDir' was not found."
}

Write-Step "Verifying CfHEE dependency"

if (-not (Test-HttpEndpoint -Url $CfheeHealthUrl)) {
    Fail "CfHEE is not reachable at '$CfheeHealthUrl'. Start CfHEE first before starting Answer Engine."
}

$cfheeHealth = Get-CfheeJson -Url $CfheeHealthUrl
if ($null -eq $cfheeHealth -or $cfheeHealth.status -ne "ok") {
    Fail "CfHEE health check did not return a valid healthy response from '$CfheeHealthUrl'."
}

$cfheeCapabilities = Get-CfheeJson -Url $CfheeCapabilitiesUrl
if (-not (Test-CfheeCapabilities -CapabilitiesResponse $cfheeCapabilities)) {
    Fail "CfHEE capabilities check failed at '$CfheeCapabilitiesUrl'. Required capabilities: scoped_retrieval=true, scope_values=true."
}

Write-Host "CfHEE is reachable and exposes the required capabilities." -ForegroundColor Green

Write-Step "Preparing backend virtual environment"

if (-not (Test-Path $BackendPython)) {
    & $pythonLauncher.Path @($pythonLauncher.Args + @("-m", "venv", $BackendVenvDir))
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $BackendPython)) {
        Fail "Failed to create backend virtual environment at '$BackendVenvDir'."
    }
    Write-Host "Created backend virtual environment." -ForegroundColor Green
}
else {
    Write-Host "Backend virtual environment already exists." -ForegroundColor DarkGreen
}

Write-Step "Ensuring backend dependencies are installed"

if (-not (Test-BackendDependenciesInstalled)) {
    Push-Location $BackendDir
    try {
        & $BackendPython -m pip install -e .
        if ($LASTEXITCODE -ne 0) {
            Fail "Backend dependency installation failed. Try '$BackendPython -m pip install -e .' inside '$BackendDir'."
        }
        Update-InstallMarker -Path $BackendDepsMarker
    }
    finally {
        Pop-Location
    }
    Write-Host "Backend dependencies installed." -ForegroundColor Green
}
else {
    Write-Host "Backend dependencies look current; skipping install." -ForegroundColor DarkGreen
}

Write-Step "Ensuring frontend dependencies are installed"

if (-not (Test-FrontendDependenciesInstalled)) {
    Push-Location $FrontendDir
    try {
        & npm.cmd install
        if ($LASTEXITCODE -ne 0) {
            Fail "Frontend dependency installation failed. Try 'npm install' inside '$FrontendDir'."
        }
        if (-not (Test-Path $FrontendNodeModules)) {
            Fail "npm reported success but '$FrontendNodeModules' was not created."
        }
        Update-InstallMarker -Path $FrontendDepsMarker
    }
    finally {
        Pop-Location
    }
    Write-Host "Frontend dependencies installed." -ForegroundColor Green
}
else {
    Write-Host "Frontend dependencies look current; skipping install." -ForegroundColor DarkGreen
}

Write-Step "Checking Ollama availability"

if (-not (Test-CommandAvailable "ollama")) {
    Write-Host "Ollama CLI was not found. The Answer Engine can still be scaffolded, but local model-backed answering will not work until Ollama is installed." -ForegroundColor Yellow
}
else {
    $ollamaTags = Invoke-OllamaTags -Url $OllamaBaseUrl
    if ($null -eq $ollamaTags) {
        Write-Host "Ollama server is not reachable at $OllamaBaseUrl. Trying to start it in a new PowerShell window..." -ForegroundColor Yellow
        Start-DevWindow -Title "Answer Engine Ollama" -WorkingDirectory $RepoRoot -Command "ollama serve"

        if (Wait-ForHttpEndpoint -Url "$OllamaBaseUrl/api/tags" -TimeoutSeconds 20) {
            Write-Host "Ollama server is reachable." -ForegroundColor Green
        }
        else {
            Write-Host "Ollama did not become reachable automatically. Start it manually with 'ollama serve' or the Ollama desktop app." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "Ollama server is reachable." -ForegroundColor DarkGreen
    }
}

Write-Step "Starting backend and frontend processes"

if (Test-HttpEndpoint -Url $HealthUrl) {
    Write-Host "Backend is already responding at $HealthUrl; not starting a second process." -ForegroundColor Yellow
}
else {
    $backendCommand = "& '$BackendPython' -m uvicorn answer_engine_backend.main:app --host 127.0.0.1 --port $BackendPort --reload"
    Start-DevWindow -Title "Answer Engine Backend" -WorkingDirectory $BackendDir -Command $backendCommand
    Write-Host "Started backend in a new PowerShell window." -ForegroundColor Green
}

if (Test-HttpEndpoint -Url $FrontendUrl) {
    Write-Host "Frontend is already responding at $FrontendUrl; not starting a second process." -ForegroundColor Yellow
}
else {
    $frontendCommand = "npm.cmd start -- --host 127.0.0.1 --port $FrontendPort"
    Start-DevWindow -Title "Answer Engine Frontend" -WorkingDirectory $FrontendDir -Command $frontendCommand
    Write-Host "Started frontend in a new PowerShell window." -ForegroundColor Green
}

Write-Step "Local development URLs"
Write-Host "Frontend:       $FrontendUrl" -ForegroundColor White
Write-Host "Backend:        $BackendUrl" -ForegroundColor White
Write-Host "API docs:       $BackendUrl/docs" -ForegroundColor White
Write-Host "Health:         $HealthUrl" -ForegroundColor White
Write-Host "CfHEE health:   $CfheeHealthUrl" -ForegroundColor White
Write-Host "CfHEE caps:     $CfheeCapabilitiesUrl" -ForegroundColor White
Write-Host "Ollama:         $OllamaBaseUrl" -ForegroundColor White