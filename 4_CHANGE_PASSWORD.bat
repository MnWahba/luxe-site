@echo off
chcp 65001 > nul 2>&1
title Change Admin Password
cls
echo.
echo  ==========================================
echo    Change Admin Password
echo  ==========================================
echo.
python scripts\change_password.py
echo.
pause
