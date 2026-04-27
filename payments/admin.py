from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'provider', 'status', 'amount', 'transaction_id', 'created_at']
    list_filter = ['provider', 'status']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['id', 'order', 'raw_response', 'created_at', 'updated_at']
