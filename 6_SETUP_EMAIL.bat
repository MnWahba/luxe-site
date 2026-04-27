@echo off
chcp 65001 > nul 2>&1
title Fancy Store - Email Setup
cls
echo.
echo  ==========================================
echo    Fancy Store - Email Setup (Gmail)
echo  ==========================================
echo.
echo  This will create your email_config.py
echo.
echo  You need:
echo  1. A Gmail account
echo  2. Gmail App Password (16 characters)
echo.
echo  To get App Password:
echo  - Go to: myaccount.google.com/apppasswords
echo  - Create password for "Mail"
echo.

set /p GMAIL_USER="Enter your Gmail address: "
set /p GMAIL_PASS="Enter App Password (16 chars, no spaces): "

echo.
echo Creating email_config.py...

(
echo EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
echo EMAIL_HOST       = 'smtp.gmail.com'
echo EMAIL_PORT       = 587
echo EMAIL_USE_TLS    = True
echo EMAIL_HOST_USER  = '%GMAIL_USER%'
echo EMAIL_HOST_PASSWORD = '%GMAIL_PASS%'
echo DEFAULT_FROM_EMAIL = 'Fancy ^<%%GMAIL_USER%%^>'
) > email_config.py

echo.
echo Testing email connection...
python -c "
import django, os, sys
os.environ['DJANGO_SETTINGS_MODULE']='luxe_bags_project.settings'
sys.path.insert(0,'.')
django.setup()
from django.core.mail import send_mail
from django.conf import settings
try:
    send_mail('Test - Fancy Store', 'Email setup successful!', settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
    print('SUCCESS! Test email sent to', settings.EMAIL_HOST_USER)
except Exception as e:
    print('ERROR:', str(e))
    print('Check your Gmail and App Password')
"

echo.
pause
