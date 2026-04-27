from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product_name', 'product_sku', 'price', 'quantity', 'total']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'total', 'status', 'payment_method', 'created_at', 'status_badge']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    list_editable = ['status']
    readonly_fields = ['order_number', 'subtotal', 'discount', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    def status_badge(self, obj):
        colors = {'pending': '#D97706', 'confirmed': '#8B5CF6', 'shipped': '#F43F5E', 'delivered': '#16A34A', 'cancelled': '#DC2626'}
        color = colors.get(obj.status, '#gray')
        return format_html('<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:12px">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.conf import settings
            try:
                msg = render_to_string('orders/emails/status_update.html', {'order': obj})
                send_mail(f'Order Update #{obj.order_number}', msg, settings.DEFAULT_FROM_EMAIL, [obj.email], html_message=msg, fail_silently=True)
            except Exception:
                pass
        super().save_model(request, obj, form, change)
