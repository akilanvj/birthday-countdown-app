@echo off
echo Starting Birthday Countdown Local Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "src\web\index.html" (
    echo Error: Please run this script from the project root directory
    echo Make sure you can see the 'src' folder from here
    pause
    exit /b 1
)

REM Start the server
python scripts\start_local.py

pause