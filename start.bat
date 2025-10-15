@echo off
echo ========================================
echo Smart Task Planner - Quick Start
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo.

echo [2/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/3] Starting Flask server...
echo.
echo ========================================
echo Server will start at http://localhost:5000
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py
