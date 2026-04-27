#!/usr/bin/env python
import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxe_bags_project.settings')
import django; django.setup()

from django.contrib.auth import get_user_model
from products.models import Category
from coupons.models import Coupon
from django.utils import timezone
import datetime

print("[1/3] Admin user...")
User = get_user_model()
if not User.objects.filter(email='admin@fancy-store.com').exists():
    User.objects.create_superuser('admin@fancy-store.com', 'admin123', full_name='Fancy Admin')
    print("    OK: admin@fancy-store.com  |  password: admin123")
else:
    print("    Already exists.")

print("[2/3] Categories...")
cats = [('Handbags','haqaib yad','handbags'),('Shoulder Bags','haqaib katf','shoulder-bags'),('Tote Bags','haqaib tote','tote-bags'),('Clutches','klatch','clutches'),('Backpacks','haqaib zahr','backpacks'),('Wallets','mahafiz','wallets')]
for en, ar, slug in cats:
    _, c = Category.objects.get_or_create(slug=slug, defaults={'name_en':en,'name_ar':en})
    if c: print(f"    + {en}")

print("[3/3] Coupons...")
for code,val,mo,d in [('WELCOME10',10,0,365),('LUXE20',20,1000,90),('FLAT50',50,0,30)]:
    if not Coupon.objects.filter(code=code).exists():
        Coupon.objects.create(code=code,discount_type='percent',discount_value=val,minimum_order=mo,valid_from=timezone.now(),valid_to=timezone.now()+datetime.timedelta(days=d),usage_limit=1000)
        print(f"    + {code}")

print("\n>>> Setup complete! <<<")
