@echo off
chcp 65001 > nul 2>&1
title Open Admin Panel
start "" "http://127.0.0.1:8000/admin/"
echo.
echo  Opening admin panel...
echo  Make sure 2_RUN.bat is running first!
echo.
echo  Email    : admin@admin@fancy-store.com
echo  Password : admin123
echo.
timeout /t 3 /nobreak > nul
