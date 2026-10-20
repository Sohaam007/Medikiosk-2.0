param(
    [switch]$NoBrowser,
    [ValidateSet('launcher', 'backend', 'frontend')]
    [string]$Service = 'launcher'
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$frontend = Join-Path $root 'frontend'
$python = Join-Path $root '.venv\Scripts\python.exe'
$backendUrl = 'http://127.0.0.1:8000/api/health'
$frontendUrl = 'http://127.0.0.1:5173'

function Test-Ready([string]$Kind) {
    try {
        if ($Kind -eq 'backend') {
            $health = Invoke-RestMethod -Uri $backendUrl -TimeoutSec 3
            return ($health.status -eq 'ok' -and $null -ne $health.version -and
                $null -ne $health.database)
        }
        $page = Invoke-WebRequest -UseBasicParsing -Uri $frontendUrl -TimeoutSec 3
        return ($page.StatusCode -eq 200 -and $page.Content.Contains('/@vite/client') -and
            $page.Content.Contains('/src/main.tsx'))
    } catch {
        return $false
    }
}

function Test-Port([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $attempt = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $attempt.AsyncWaitHandle.WaitOne(500)) { return $false }
        $client.EndConnect($attempt)
        return $true
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

function Start-ServiceWindow([string]$Kind) {
    $arguments = '-NoLogo -NoProfile -NoExit -ExecutionPolicy Bypass -File "{0}" -Service {1}' -f $PSCommandPath, $Kind
    Start-Process -FilePath 'powershell.exe' -ArgumentList $arguments -WorkingDirectory $root | Out-Null
}

try {
    if (-not (Test-Path -LiteralPath (Join-Path $root 'pyproject.toml')) -or
        -not (Test-Path -LiteralPath (Join-Path $frontend 'package.json'))) {
        throw 'Keep start_dev.bat and start_dev.ps1 in the MediKiosk project root.'
    }

    # Worker windows run in their own directories; no machine-specific paths.
    if ($Service -eq 'backend') {
        $Host.UI.RawUI.WindowTitle = 'MediKiosk Backend - Ctrl+C to stop'
        Set-Location -LiteralPath $root
        & $python -m uvicorn medikiosk.api.app:create_app --factory --reload --host 127.0.0.1 --port 8000
        if ($LASTEXITCODE -ne 0) { throw 'Backend exited with an error.' }
        exit 0
    }
    if ($Service -eq 'frontend') {
        $Host.UI.RawUI.WindowTitle = 'MediKiosk Frontend - Ctrl+C to stop'
        Set-Location -LiteralPath $frontend
        & npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort
        if ($LASTEXITCODE -ne 0) { throw 'Frontend exited with an error.' }
        exit 0
    }

    $backendReady = Test-Ready 'backend'
    $frontendReady = Test-Ready 'frontend'
    if (-not $backendReady -and (Test-Port 8000)) {
        throw 'Port 8000 is occupied but the MediKiosk health check failed. Close that service and retry.'
    }
    if (-not $frontendReady -and (Test-Port 5173)) {
        throw 'Port 5173 is occupied but the Vite check failed. Close that service and retry.'
    }

    # First launch can install locked project dependencies. Never overwrite .env.
    if (-not $backendReady -and -not (Test-Path -LiteralPath $python)) {
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
            throw 'uv is missing. Install uv and Python 3.11.9, then try again.'
        }
        Push-Location -LiteralPath $root
        try {
            & uv sync --frozen --extra dev
            if ($LASTEXITCODE -ne 0) { throw 'Python dependency setup failed.' }
        } finally { Pop-Location }
    }
    if (-not $frontendReady) {
        if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
            throw 'npm is missing. Install the Node version listed in .nvmrc, then try again.'
        }
        if (-not (Test-Path -LiteralPath (Join-Path $frontend 'node_modules\vite\bin\vite.js'))) {
            Push-Location -LiteralPath $frontend
            try {
                & npm.cmd ci
                if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency setup failed.' }
            } finally { Pop-Location }
        }
    }

    # The copied .env.example intentionally leaves API_KEY blank. For this
    # local-only launcher, provide the same non-production development value as
    # the application's development default so the demo token endpoint works.
    # These process-scoped values are never written to disk or used in production.
    if ([string]::IsNullOrWhiteSpace($env:API_KEY)) {
        $env:API_KEY = 'medikiosk-dev-secret-key-32chars-minimum-entropy'
    }
    if ([string]::IsNullOrWhiteSpace($env:JWT_SECRET_KEY)) {
        $env:JWT_SECRET_KEY = $env:API_KEY
    }

    if ($backendReady) { Write-Host 'Reusing responding backend on port 8000.' }
    else { Start-ServiceWindow 'backend' }
    if ($frontendReady) { Write-Host 'Reusing responding Vite server on port 5173.' }
    else { Start-ServiceWindow 'frontend' }

    Write-Host 'Waiting for backend and frontend readiness...'
    $deadline = (Get-Date).AddSeconds(60)
    do {
        $backendReady = Test-Ready 'backend'
        $frontendReady = Test-Ready 'frontend'
        if ($backendReady -and $frontendReady) { break }
        Start-Sleep -Seconds 1
    } while ((Get-Date) -lt $deadline)
    if (-not ($backendReady -and $frontendReady)) {
        throw 'Startup did not become ready within 60 seconds. Check the two server windows for errors.'
    }

    Write-Host "Ready: $frontendUrl" -ForegroundColor Green
    Write-Host "API health: $backendUrl"
    Write-Host 'Local demo only. Use synthetic data. Stop both servers with Ctrl+C in their windows.'
    if (-not $NoBrowser) { Start-Process $frontendUrl }
} catch {
    Write-Host "Startup failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
