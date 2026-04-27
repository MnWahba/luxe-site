@echo off
chcp 65001 > nul 2>&1
title Fancy فانسي - Server Running
cls

REM ---- Check DB exists ----
if not exist db.sqlite3 (
    echo.
    echo  [!] Database not found.
    echo  Please run 1_INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

cls
echo.
echo  ==========================================
echo    Fancy فانسي  -  Server Started
echo  ==========================================
echo.
echo   Website  :  http://127.0.0.1:8000
echo   Admin    :  http://127.0.0.1:8000/admin/
echo   Email    :  admin@admin@fancy-store.com
echo   Password :  admin123
echo.
echo   Press CTRL+C to stop the server
echo  ==========================================
echo.

REM Open browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak > nul && start http://127.0.0.1:8000"

python manage.py runserver 127.0.0.1:8000

echo.
echo  Server stopped.
pause
