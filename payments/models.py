from django.db import models
from orders.models import Order
import uuid


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'), (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'), (STATUS_REFUNDED, 'Refunded'),
    ]
    PROVIDER_COD = 'cod'
    PROVIDER_PAYMOB = 'paymob'
    PROVIDER_FAWRY = 'fawry'
    PROVIDER_CHOICES = [
        (PROVIDER_COD, 'Cash on Delivery'),
        (PROVIDER_PAYMOB, 'Paymob'),
        (PROVIDER_FAWRY, 'Fawry'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True)
    provider_reference = models.CharField(max_length=255, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider} - {self.order.order_number} - {self.status}"
