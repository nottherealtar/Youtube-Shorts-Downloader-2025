@echo off
echo ========================================
echo YouTube Downloader Pro - Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo [OK] pip is available
echo.

REM Install Python dependencies
echo ========================================
echo Installing Python dependencies...
echo ========================================
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo [OK] Python dependencies installed
echo.

REM Check if FFmpeg is installed
echo ========================================
echo Checking for FFmpeg...
echo ========================================
echo.

REM Refresh PATH
call refreshenv >nul 2>&1

ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg is not installed
    echo.
    echo FFmpeg is required for video processing
    echo.
    set /p INSTALL_FFMPEG="Do you want to install FFmpeg now? (Y/N): "
    
    if /i "%INSTALL_FFMPEG%"=="Y" (
        echo.
        echo Installing FFmpeg via winget...
        winget install ffmpeg
        
        if errorlevel 1 (
            echo [ERROR] Failed to install FFmpeg
            echo Please install manually from: https://ffmpeg.org/download.html
            echo Or run: winget install ffmpeg
        ) else (
            echo [OK] FFmpeg installed successfully
            echo NOTE: You may need to restart your terminal for FFmpeg to work
        )
    ) else (
        echo.
        echo [WARNING] Skipping FFmpeg installation
        echo You can install it later with: winget install ffmpeg
    )
) else (
    echo [OK] FFmpeg is already installed
    ffmpeg -version | findstr "ffmpeg version"
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the application:
echo   python app.py
echo.
echo Or simply double-click: run.bat
echo.
pause
