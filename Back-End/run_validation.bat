@echo off
REM Step 4 Validation - Complete Test Suite Launcher
REM This script guides users through the entire validation process

setlocal enabledelayedexpansion

cd /d "%~dp0"

:menu
cls
echo.
echo ============================================================================
echo ATLS Step 4 Validation Test Suite
echo ============================================================================
echo.
echo What would you like to do?
echo.
echo   1 - Start Backend Server
echo   2 - Prepare Database (Create test data if missing)
echo   3 - Run Validation Tests
echo   4 - View Test Results Documentation
echo   5 - Open Django Admin
echo   6 - Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto start_server
if "%choice%"=="2" goto prepare_db
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto view_docs
if "%choice%"=="5" goto admin
if "%choice%"=="6" goto end
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:start_server
cls
echo.
echo ============================================================================
echo Starting Django Development Server
echo ============================================================================
echo.
echo Server will run at: http://localhost:8000/
echo Press Ctrl+C to stop the server
echo.
timeout /t 2 >nul

call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
pause
goto menu

:prepare_db
cls
echo.
echo ============================================================================
echo Preparing Test Database
echo ============================================================================
echo.

call venv\Scripts\activate.bat
python prepare_test_data.py

if errorlevel 1 (
    echo.
    echo Database preparation failed. Please check the errors above.
) else (
    echo.
    echo Database preparation successful!
    echo You can now run validation tests.
)

pause
goto menu

:run_tests
cls
echo.
echo ============================================================================
echo Running Validation Tests
echo ============================================================================
echo.
echo Ensure the backend server is running (choose option 1 if not)
echo.
timeout /t 2 >nul

call venv\Scripts\activate.bat
python validate_step4.py

echo.
echo.
echo Test execution complete. Review results above.
pause
goto menu

:view_docs
cls
echo.
echo ============================================================================
echo Test Results Documentation
echo ============================================================================
echo.
echo The following documentation files are available:
echo.
echo   VALIDATION_CHECKLIST.md ... Step-by-step testing guide
echo   TESTING_README.md ......... How-to + troubleshooting
echo   VALIDATION_PLAN.md ....... Detailed procedures
echo.
echo Opening browser to view documentation...
echo.
start http://localhost:8000/api/

pause
goto menu

:admin
cls
echo.
echo ============================================================================
echo Django Admin Interface
echo ============================================================================
echo.
echo Opening Django Admin at: http://localhost:8000/admin/
echo.
echo Login credentials:
echo   Email: admin@example.com
echo   Password: admin
echo.
start http://localhost:8000/admin/

pause
goto menu

:end
cls
echo.
echo Thank you for using ATLS Validation Suite
echo.
exit /b 0
