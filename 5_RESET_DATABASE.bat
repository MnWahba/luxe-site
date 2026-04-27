@echo off
chcp 65001 > nul 2>&1
title Reset Database
cls
echo.
echo  ==========================================
echo    RESET DATABASE
echo  ==========================================
echo.
echo  WARNING: This will delete ALL data!
echo  (orders, users, products, etc.)
echo.
set /p CONFIRM="Type YES to confirm: "
if /i "%CONFIRM%" neq "YES" (
    echo  Cancelled.
    pause
    exit /b
)
echo.
python scripts\reset_db.py
echo.
pause
