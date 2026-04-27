#!/usr/bin/env python
import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxe_bags_project.settings')
import django; django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = input("Enter admin email [admin@fancy-store.com]: ").strip() or 'admin@fancy-store.com'
try:
    user = User.objects.get(email=email)
    pwd = input("New password: ").strip()
    user.set_password(pwd)
    user.save()
    print(f"Password changed for {email}")
except User.DoesNotExist:
    print(f"User {email} not found")
