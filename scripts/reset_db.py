#!/usr/bin/env python
import os, sys, shutil
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

confirm = input("This will DELETE all data. Type YES to confirm: ")
if confirm.strip().upper() != 'YES':
    print("Cancelled.")
    sys.exit()

db_path = os.path.join(BASE, 'db.sqlite3')
if os.path.exists(db_path):
    os.remove(db_path)
    print("Database deleted.")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxe_bags_project.settings')
import django; django.setup()
from django.core.management import call_command
call_command('migrate', '--run-syncdb')

# Re-run setup
exec(open(os.path.join(BASE, 'scripts', 'setup_db.py')).read())
