@echo off
REM Unified Trading Terminal Startup Script for Windows

echo 🔥 UNIFIED TRADING TERMINAL LAUNCHER
echo =====================================

REM Set Python path
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run the unified launcher
echo 🚀 Starting Unified Trading Terminal...
python unified_launcher.py

echo 👋 Unified Trading Terminal stopped
pause
