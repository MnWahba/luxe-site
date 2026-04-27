#!/bin/bash
echo "======================================"
echo "  Luxe Bags - Setup Script"
echo "======================================"

# Install dependencies
echo "[1/5] Installing requirements..."
pip install -r requirements.txt

# Run migrations
echo "[2/5] Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "[3/5] Creating superuser..."
echo "from django.contrib.auth import get_user_model; U = get_user_model(); U.objects.filter(email='admin@luxebags.com').exists() or U.objects.create_superuser('admin@luxebags.com', 'admin123', full_name='Admin')" | python manage.py shell

# Collect static files
echo "[4/5] Collecting static files..."
python manage.py collectstatic --noinput --verbosity 0

# Create sample data
echo "[5/5] Creating sample data..."
python manage.py shell << 'PYEOF'
from products.models import Category, Product

if not Category.objects.exists():
    cats = [
        Category(name_en='Handbags', name_ar='حقائب يد', slug='handbags'),
        Category(name_en='Shoulder Bags', name_ar='حقائب كتف', slug='shoulder-bags'),
        Category(name_en='Tote Bags', name_ar='حقائب توت', slug='tote-bags'),
        Category(name_en='Clutches', name_ar='كلاتش', slug='clutches'),
        Category(name_en='Backpacks', name_ar='حقائب ظهر', slug='backpacks'),
        Category(name_en='Wallets', name_ar='محافظ', slug='wallets'),
    ]
    Category.objects.bulk_create(cats)
    print("Categories created.")

if not Product.objects.exists():
    from decimal import Decimal
    cat = Category.objects.first()
    products = [
        Product(category=cat, name_en='Classic Leather Handbag', name_ar='حقيبة يد جلدية كلاسيكية',
                description_en='Timeless elegance meets modern sophistication in this hand-crafted leather piece.',
                description_ar='أناقة خالدة تلتقي بالتطور الحديث في هذه القطعة الجلدية المصنوعة يدوياً.',
                price=Decimal('1299'), discount_price=Decimal('999'), stock=15, is_featured=True, is_new_arrival=True,
                material_en='Genuine Leather'),
        Product(category=cat, name_en='Rose Gold Chain Bag', name_ar='حقيبة سلسلة ذهبي وردي',
                description_en='Dazzling rose gold hardware with plush velvet interior.',
                description_ar='إكسسوارات ذهبية وردية رائعة مع بطانة مخملية فاخرة.',
                price=Decimal('899'), stock=10, is_featured=True,
                material_en='Vegan Leather'),
        Product(category=cat, name_en='Midnight Velvet Clutch', name_ar='كلاتش مخملي منتصف الليل',
                description_en='Perfect for evening affairs. Deep midnight velvet with crystal closure.',
                description_ar='مثالية للمناسبات المسائية. مخمل أزرق داكن مع إغلاق كريستالي.',
                price=Decimal('599'), discount_price=Decimal('449'), stock=20, is_featured=True,
                material_en='Velvet'),
        Product(category=cat, name_en='Structured Work Tote', name_ar='حقيبة توت للعمل',
                description_en='Carry your essentials in style. Spacious and professional.',
                description_ar='احملي أغراضك الأساسية بأناقة. واسعة ومهنية.',
                price=Decimal('1599'), stock=8,
                material_en='Full-Grain Leather'),
    ]
    Product.objects.bulk_create(products)
    print("Sample products created.")

from coupons.models import Coupon
from django.utils import timezone
import datetime
if not Coupon.objects.exists():
    Coupon.objects.create(
        code='WELCOME10',
        discount_type='percent',
        discount_value=10,
        valid_from=timezone.now(),
        valid_to=timezone.now() + datetime.timedelta(days=365),
        usage_limit=1000,
    )
    Coupon.objects.create(
        code='LUXE20',
        discount_type='percent',
        discount_value=20,
        minimum_order=1000,
        valid_from=timezone.now(),
        valid_to=timezone.now() + datetime.timedelta(days=90),
        usage_limit=500,
    )
    print("Sample coupons created: WELCOME10 (10%), LUXE20 (20% on orders 1000+ EGP)")
PYEOF

echo ""
echo "======================================"
echo "  SETUP COMPLETE!"
echo "======================================"
echo ""
echo "  Admin: http://127.0.0.1:8000/admin/"
echo "  Email: admin@luxebags.com"
echo "  Password: admin123"
echo ""
echo "  Run: python manage.py runserver"
echo "======================================"
