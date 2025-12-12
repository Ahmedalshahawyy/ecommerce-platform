# Run all tests (backend unit, integration, frontend e2e) on Windows PowerShell
# Usage: .\scripts\run_all_tests.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# Ensure clean DBs
if (Test-Path "$ProjectRoot\ecommerce.db") { Remove-Item "$ProjectRoot\ecommerce.db" -Force }
if (Test-Path "$ProjectRoot\backend\ecommerce.db") { Remove-Item "$ProjectRoot\backend\ecommerce.db" -Force }
if (Test-Path "$ProjectRoot\ecommerce_test.db") { Remove-Item "$ProjectRoot\ecommerce_test.db" -Force }

# Install backend deps
Push-Location "$ProjectRoot\backend"
python -m pip install --upgrade pip
pip install -r requirements.txt
Pop-Location

# Run backend unit tests
Write-Host "Running backend unit tests..."
$env:PYTHONPATH = $ProjectRoot
python -m pytest backend/tests/test_api.py -q -vv
if ($LASTEXITCODE -ne 0) { Exit $LASTEXITCODE }

# Run backend tests (unit + integration) with coverage
Write-Host "Running backend tests (unit + integration) with coverage..."
Push-Location $ProjectRoot
$env:DATABASE_URL = "sqlite:///./ecommerce_test.db"
$env:PYTHONPATH = $ProjectRoot
$uvicornProc = Start-Process -FilePath python -ArgumentList '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000' -PassThru
Start-Sleep -Seconds 2
# Wait for backend health endpoint
function Wait-ForUrl {
    param($url, $timeoutSec)
    $start = Get-Date
    while ((Get-Date) - $start -lt (New-TimeSpan -Seconds $timeoutSec)) {
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 5 -ErrorAction Stop
            if ($r.StatusCode -eq 200) { return $true }
        } catch { }
        Start-Sleep -Seconds 1
    }
    return $false
}
if (-not (Wait-ForUrl -url 'http://127.0.0.1:8000/health' -timeoutSec 30)) {
    Write-Error "Backend failed to start"
    Stop-Process -Id $uvicornProc.Id -Force -ErrorAction SilentlyContinue
    Exit 2
}
try {
    python -m pytest --cov=backend --cov-report=xml:coverage.xml backend/tests -q -vv
    if ($LASTEXITCODE -ne 0) { throw "Backend tests failed with $LASTEXITCODE" }
} finally {
    Stop-Process -Id $uvicornProc.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    if (Test-Path "$ProjectRoot\ecommerce_test.db") { Remove-Item "$ProjectRoot\ecommerce_test.db" -Force }
    Pop-Location
}

# Run frontend e2e tests
Write-Host "Running frontend e2e tests..."
Push-Location "$ProjectRoot\frontend"
if ($env:SKIP_E2E -eq '1') {
    Write-Host "SKIP_E2E=1 set; skipping frontend e2e tests."
    Pop-Location
} else {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        if ($env:FORCE_E2E -eq '1') {
            Write-Error "npm is not available in PATH and FORCE_E2E=1; failing."
            Exit 2
        }
        Write-Warning "npm is not available in PATH; skipping frontend e2e tests."
        Pop-Location
    } else {
        npm install
        npx playwright install --with-deps
        $env:PYTHONPATH = $ProjectRoot
        $backendProc = Start-Process -FilePath python -ArgumentList '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000' -PassThru
        Start-Sleep -Seconds 2
        $frontendProc = Start-Process -FilePath npm -ArgumentList 'run', 'dev' -PassThru
        Start-Sleep -Seconds 4
        try {
            & npm run test:e2e --if-present
            $e2erc = $LASTEXITCODE
            if ($e2erc -ne 0) { throw "E2E tests failed with $e2erc" }
        } finally {
            Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue
            Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
            Pop-Location
        }
    }
}

Write-Host "All tests completed."
