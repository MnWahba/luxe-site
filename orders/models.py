from django.db import models
from django.conf import settings
from products.models import Product
from coupons.models import Coupon
import uuid


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    PAYMENT_COD = 'cod'
    PAYMENT_PAYMOB = 'paymob'
    PAYMENT_FAWRY = 'fawry'
    PAYMENT_METHODS = [
        (PAYMENT_COD, 'Cash on Delivery'),
        (PAYMENT_PAYMOB, 'Online Payment (Paymob)'),
        (PAYMENT_FAWRY, 'Fawry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    governorate = models.CharField(max_length=100)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default=PAYMENT_COD)
    payment_status = models.CharField(max_length=20, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"LB-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    def get_status_display_ar(self):
        ar_map = {
            'pending': 'قيد الانتظار', 'confirmed': 'مؤكد',
            'shipped': 'تم الشحن', 'delivered': 'تم التسليم', 'cancelled': 'ملغي'
        }
        return ar_map.get(self.status, self.status)

    STATUS_COLORS = {
        'pending': 'warning', 'confirmed': 'primary',
        'shipped': 'secondary', 'delivered': 'success', 'cancelled': 'danger'
    }

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'gray')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        from decimal import Decimal as _D
        self.total = _D(str(self.price)) * int(self.quantity)
        super().save(*args, **kwargs)
