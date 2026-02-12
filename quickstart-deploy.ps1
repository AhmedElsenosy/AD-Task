# Windows Server Deployment Quick Start Script (PowerShell)
# Run this in PowerShell as Administrator on your Windows Server
#
# Usage:
#   1. Right-click PowerShell and select "Run as Administrator"
#   2. Navigate to your project folder: cd C:\WebApps\AD-Task
#   3. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   4. Run: .\quickstart-deploy.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Active Directory Integration - Quick Deploy" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$admin = [Security.Principal.WindowsIdentity]::GetCurrent()
$adminRole = New-Object Security.Principal.WindowsPrincipal($admin)
if (-not $adminRole.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: Please run this as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 1: Check Python
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ first from https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "OK: Python is installed - $pythonCheck" -ForegroundColor Green

# Step 2: Create virtual environment
Write-Host ""
Write-Host "[2/8] Creating/checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "OK: Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "OK: Virtual environment created" -ForegroundColor Green
}

# Step 3: Activate virtual environment
Write-Host ""
Write-Host "[3/8] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "OK: Virtual environment activated" -ForegroundColor Green

# Step 4: Upgrade pip
Write-Host ""
Write-Host "[4/8] Upgrading pip and setuptools..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "OK: pip upgraded" -ForegroundColor Green

# Step 5: Install requirements
Write-Host ""
Write-Host "[5/8] Installing Python dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements!" -ForegroundColor Red
    Write-Host "Check the error messages above and fix any issues" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "OK: All dependencies installed" -ForegroundColor Green

# Step 6: Collect static files
Write-Host ""
Write-Host "[6/8] Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to collect static files!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "OK: Static files collected" -ForegroundColor Green

# Step 7: Migrate database
Write-Host ""
Write-Host "[7/8] Running database migrations..." -ForegroundColor Yellow
Write-Host "This will create all required tables in your database..." -ForegroundColor Cyan
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to run migrations!" -ForegroundColor Red
    Write-Host "Please check your database configuration in the .env file:" -ForegroundColor Yellow
    Write-Host "  - DB_HOST: SQL Server hostname/IP" -ForegroundColor Cyan
    Write-Host "  - DB_USER: Database username" -ForegroundColor Cyan
    Write-Host "  - DB_PASSWORD: Database password" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "OK: Database migrations completed" -ForegroundColor Green

# Step 8: Test with Gunicorn
Write-Host ""
Write-Host "[8/8] Testing application with Gunicorn..." -ForegroundColor Yellow
Write-Host "Starting Gunicorn (wait for 'Listening at' message)..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing server starting on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server after testing" -ForegroundColor Yellow
Write-Host ""

gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 300 core.wsgi:application

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Deployment Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Verify the application loaded successfully" -ForegroundColor White
Write-Host "  2. Open browser to http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  3. Check admin interface at http://127.0.0.1:8000/admin" -ForegroundColor White
Write-Host "  4. Test login with your credentials" -ForegroundColor White
Write-Host "  5. Stop this server (Ctrl+C)" -ForegroundColor White
Write-Host "  6. Configure IIS (see DEPLOYMENT_WINDOWS_SERVER.md)" -ForegroundColor White
Write-Host ""

Write-Host "Important documentation:" -ForegroundColor Cyan
Write-Host "  - DEPLOYMENT_WINDOWS_SERVER.md (Complete step-by-step guide)" -ForegroundColor White
Write-Host "  - DEPLOYMENT_CHECKLIST.md (Validation checklist)" -ForegroundColor White
Write-Host "  - .env.production (Production settings template)" -ForegroundColor White
Write-Host "  - web.config (IIS configuration)" -ForegroundColor White
Write-Host ""

Write-Host "For questions, refer to the documentation or the README.md file." -ForegroundColor Yellow
Write-Host ""
