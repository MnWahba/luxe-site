from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_FIXED = 'fixed'
    DISCOUNT_PERCENT = 'percent'
    DISCOUNT_TYPES = [(DISCOUNT_FIXED, 'Fixed Amount'), (DISCOUNT_PERCENT, 'Percentage')]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default=DISCOUNT_PERCENT)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            self.usage_count < self.usage_limit
        )

    def calculate_discount(self, order_total):
        if not self.is_valid or order_total < self.minimum_order:
            return 0
        if self.discount_type == self.DISCOUNT_PERCENT:
            discount = (order_total * self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        return min(self.discount_value, order_total)


class Meta:
    verbose_name = 'Coupon'
    verbose_name_plural = 'Coupons'
