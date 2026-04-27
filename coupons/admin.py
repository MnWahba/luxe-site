from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'usage_count', 'usage_limit', 'is_active']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code']
    list_editable = ['is_active']
