@echo off
echo Starting YouTube Downloader Pro...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Run the application
python app.py

REM If the app exits with an error, pause to see the error message
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error
    pause
)
