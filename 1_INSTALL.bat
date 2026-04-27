@echo off
chcp 65001 > nul 2>&1
title Fancy فانسي - Install
cls
echo.
echo  ==========================================
echo    Fancy فانسي  -  First Time Setup
echo  ==========================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [ERROR] Python not found!
    echo.
    echo  Download from: https://python.org/downloads
    echo  Check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
)

echo  Python found:
python --version
echo.

echo  [1/4] Upgrading pip...
python -m pip install --upgrade pip --quiet 2>nul

echo  [2/4] Installing packages...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERROR] pip install failed.
    echo  Try: Right-click 1_INSTALL.bat, Run as Administrator
    echo.
    pause
    exit /b 1
)

echo.
echo  [3/4] Creating database...
python manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo  [ERROR] Migration failed.
    pause
    exit /b 1
)

echo.
echo  [4/4] Creating admin + sample data...
python scripts\setup_db.py
if %ERRORLEVEL% neq 0 (
    echo  [ERROR] Setup failed.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo    DONE! Installation complete.
echo  ==========================================
echo.
echo   Login  :  admin@admin@fancy-store.com
echo   Pass   :  admin123
echo.
echo   Next step: run  2_RUN.bat
echo.
pause
