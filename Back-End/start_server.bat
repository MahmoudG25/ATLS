@echo off
REM ==============================================================================
REM ATLS-V2 Django Backend API Test Script
REM ==============================================================================
REM This script starts the Django server and tests the API endpoints
REM Usage: Run this script from the Back-End directory or modify paths as needed
REM ==============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo ATLS-V2 Django Backend - API Test Script
echo ============================================================================
echo.

REM Set the backend directory
set BACKEND_DIR=e:\web\project------------\ATLS-V2\Back-End

REM Change to backend directory
cd /d "%BACKEND_DIR%"

if not exist "manage.py" (
    echo ERROR: manage.py not found in %BACKEND_DIR%
    echo Please verify the path and try again.
    exit /b 1
)

echo [1/4] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at venv\Scripts\activate.bat
    exit /b 1
)
echo OK - Virtual environment found

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Starting Django server...
echo Server will run on http://localhost:8000
echo Press CTRL+C to stop the server when done testing
echo.
echo Starting server...
timeout /t 2 /nobreak

REM Start Django server
python manage.py runserver 0.0.0.0:8000

REM If we get here, server was stopped
echo.
echo Server stopped.
pause
