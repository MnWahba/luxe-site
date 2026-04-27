from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta


class LuxeBagsAdminSite(admin.AdminSite):
    site_header = '✦ Fancy فانسي — Admin'
    site_title = 'Fancy فانسي'
    index_title = 'لوحة التحكم — Dashboard'
    login_template = None

    def get_urls(self):
        urls = super().get_urls()
        extra = [path('analytics/', self.admin_view(self.analytics_view), name='analytics')]
        return extra + urls

    def analytics_view(self, request):
        from orders.models import Order
        from products.models import Product
        from users.models import CustomUser
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0)
        data = {
            'total_orders': Order.objects.count(),
            'month_orders': Order.objects.filter(created_at__gte=month_start).count(),
            'total_revenue': float(Order.objects.filter(status='delivered').aggregate(t=Sum('total'))['t'] or 0),
            'month_revenue': float(Order.objects.filter(status='delivered', created_at__gte=month_start).aggregate(t=Sum('total'))['t'] or 0),
            'total_products': Product.objects.filter(is_active=True).count(),
            'low_stock': Product.objects.filter(stock__lt=5, is_active=True).count(),
            'total_users': CustomUser.objects.count(),
            'month_users': CustomUser.objects.filter(date_joined__gte=month_start).count(),
        }
        return JsonResponse(data)

    def index(self, request, extra_context=None):
        from orders.models import Order
        from products.models import Product
        from users.models import CustomUser
        from core.models import SiteSettings
        now = timezone.now()
        extra_context = extra_context or {}
        extra_context.update({
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'total_revenue': Order.objects.filter(status='delivered').aggregate(t=Sum('total'))['t'] or 0,
            'total_products': Product.objects.filter(is_active=True).count(),
            'low_stock_products': Product.objects.filter(stock__lt=5, is_active=True).count(),
            'total_users': CustomUser.objects.count(),
            'recent_orders': Order.objects.order_by('-created_at')[:5],
            'sales_report_url': '/admin/core/sales/',
        })
        return super().index(request, extra_context)


admin_site = LuxeBagsAdminSite(name='admin')
