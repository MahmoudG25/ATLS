# ==============================================================================
# ATLS-V2 Django Backend API Testing Suite
# ==============================================================================
# This PowerShell script starts the Django server and provides testing commands
# Usage: .\test_api.ps1
# ==============================================================================

Write-Host "`n" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ATLS-V2 Django Backend - API Testing Suite" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BackendDir = "e:\web\project------------\ATLS-V2\Back-End"
$ServerUrl = "http://localhost:8000"
$LoginEndpoint = "/api/auth/login/"
$FarmEndpoint = "/api/farm/farms/"

# Test credentials
$TestEmail = "admin@example.com"
$TestPassword = "admin"

# Change to backend directory
Set-Location $BackendDir

if (-not (Test-Path "manage.py")) {
    Write-Host "ERROR: manage.py not found in $BackendDir" -ForegroundColor Red
    exit 1
}

Write-Host "[1/5] Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Virtual environment found" -ForegroundColor Green

Write-Host "`n[2/5] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "OK - Virtual environment activated" -ForegroundColor Green

Write-Host "`n[3/5] Starting Django server in background..." -ForegroundColor Yellow
Write-Host "Server URL: $ServerUrl" -ForegroundColor Cyan
Write-Host ""

# Start Django server in background
$djangoProcess = Start-Process -FilePath "python" -ArgumentList "manage.py runserver 0.0.0.0:8000" -PassThru -NoNewWindow

# Wait for server to start
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if server started
if ($djangoProcess.HasExited) {
    Write-Host "ERROR: Django server failed to start" -ForegroundColor Red
    exit 1
}

Write-Host "OK - Django server started (PID: $($djangoProcess.Id))" -ForegroundColor Green

Write-Host "`n[4/5] Testing API endpoints..." -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan

# Test 1: Login Endpoint
Write-Host "`nTest 1: Login Endpoint" -ForegroundColor Cyan
Write-Host "POST $ServerUrl$LoginEndpoint" -ForegroundColor White
Write-Host "Credentials: email=$TestEmail, password=$TestPassword" -ForegroundColor Gray

$loginBody = @{
    email = $TestEmail
    password = $TestPassword
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$ServerUrl$LoginEndpoint" `
                                        -Method Post `
                                        -ContentType "application/json" `
                                        -Body $loginBody `
                                        -ErrorAction Stop
    
    Write-Host "Status: 200 OK" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    Write-Host ($loginResponse | ConvertTo-Json -Depth 3) -ForegroundColor Gray
    
    # Extract access token
    $accessToken = $loginResponse.access
    Write-Host "`nAccess Token (first 50 chars): $($accessToken.Substring(0, 50))..." -ForegroundColor Yellow
    
    # Test 2: Farm List Endpoint
    Write-Host "`n================================================================" -ForegroundColor Cyan
    Write-Host "Test 2: Farm List Endpoint" -ForegroundColor Cyan
    Write-Host "GET $ServerUrl$FarmEndpoint" -ForegroundColor White
    Write-Host "Authorization: Bearer <token>" -ForegroundColor Gray
    
    $headers = @{
        Authorization = "Bearer $accessToken"
    }
    
    try {
        $farmsResponse = Invoke-RestMethod -Uri "$ServerUrl$FarmEndpoint" `
                                           -Method Get `
                                           -Headers $headers `
                                           -ErrorAction Stop
        
        Write-Host "Status: 200 OK" -ForegroundColor Green
        Write-Host "Response:" -ForegroundColor White
        Write-Host ($farmsResponse | ConvertTo-Json -Depth 3) -ForegroundColor Gray
        
        if ($farmsResponse -is [array]) {
            Write-Host "`nNumber of farms: $($farmsResponse.Count)" -ForegroundColor Yellow
        } else {
            Write-Host "`nResponse is not an array" -ForegroundColor Yellow
        }
        
        Write-Host "`n✓ FARM LIST TEST PASSED" -ForegroundColor Green
        
    } catch {
        Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        try {
            $errorResponse = $_ | ConvertFrom-Json
            Write-Host "Error Details: $($errorResponse | ConvertTo-Json)" -ForegroundColor Gray
        } catch {}
    }
    
    Write-Host "`n✓ LOGIN TEST PASSED" -ForegroundColor Green
    
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    try {
        $errorResponse = $_ | ConvertFrom-Json
        Write-Host "Error Details: $($errorResponse | ConvertTo-Json)" -ForegroundColor Gray
    } catch {}
    Write-Host "`n✗ LOGIN TEST FAILED" -ForegroundColor Red
}

Write-Host "`n[5/5] Cleaning up..." -ForegroundColor Yellow

# Stop Django server
if ($djangoProcess -and -not $djangoProcess.HasExited) {
    Stop-Process -Id $djangoProcess.Id -Force
    Write-Host "Django server stopped" -ForegroundColor Green
}

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "API Testing Complete" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
