from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from django.http import JsonResponse
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product
from users.models import CustomUser


@staff_member_required
def sales_report_view(request):
    return render(request, 'admin/core/sales_report.html')


@staff_member_required
def kpis_api(request):
    days = int(request.GET.get('period', 30))
    since = timezone.now() - timedelta(days=days)

    orders = Order.objects.filter(created_at__gte=since)
    revenue_orders = orders.filter(status__in=['confirmed', 'shipped', 'delivered'])

    total_revenue = revenue_orders.aggregate(t=Sum('total'))['t'] or 0
    total_orders = orders.count()
    delivered = orders.filter(status='delivered').count()
    pending = orders.filter(status='pending').count()
    confirmed = orders.filter(status='confirmed').count()
    shipped = orders.filter(status='shipped').count()
    cancelled = orders.filter(status='cancelled').count()

    avg_order = revenue_orders.aggregate(a=Avg('total'))['a'] or 0
    units_sold = OrderItem.objects.filter(
        order__created_at__gte=since,
        order__status__in=['confirmed', 'shipped', 'delivered']
    ).aggregate(u=Sum('quantity'))['u'] or 0

    total_customers = CustomUser.objects.count()
    new_customers = CustomUser.objects.filter(date_joined__gte=since).count()

    return JsonResponse({
        'revenue': float(total_revenue),
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
        'confirmed': confirmed,
        'shipped': shipped,
        'cancelled': cancelled,
        'avg_order': float(avg_order),
        'units_sold': units_sold,
        'total_customers': total_customers,
        'new_customers': new_customers,
    })


@staff_member_required
def sales_data_api(request):
    from django.db.models.functions import TruncDate
    days = int(request.GET.get('period', 30))
    since = timezone.now() - timedelta(days=days)

    daily = list(
        Order.objects.filter(
            created_at__gte=since,
            status__in=['confirmed', 'shipped', 'delivered']
        ).annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(revenue=Sum('total'), count=Count('id'))
        .order_by('day')
    )

    top_products = list(
        OrderItem.objects.filter(
            order__created_at__gte=since,
            order__status__in=['confirmed', 'shipped', 'delivered']
        ).values('product_name')
        .annotate(units=Sum('quantity'), revenue=Sum('total'))
        .order_by('-units')[:8]
    )

    cat_sales = list(
        OrderItem.objects.filter(
            order__created_at__gte=since,
            order__status__in=['confirmed', 'shipped', 'delivered']
        ).values(cat_name=F('product__category__name_en'))
        .annotate(units=Sum('quantity'), revenue=Sum('total'))
        .order_by('-revenue')[:6]
    )

    return JsonResponse({
        'daily': daily,
        'top_products': top_products,
        'categories': cat_sales,
    }, default=str)


@staff_member_required
def recent_orders_api(request):
    orders = list(
        Order.objects.order_by('-created_at')[:20]
        .values('id', 'order_number', 'full_name', 'total', 'status', 'created_at')
    )
    return JsonResponse({'orders': orders}, default=str)


@staff_member_required
def low_stock_api(request):
    threshold = int(request.GET.get('threshold', 5))
    products = list(
        Product.objects.filter(stock__lte=threshold, is_active=True)
        .order_by('stock')
        .values('id', 'name_en', 'sku', 'stock')[:20]
    )
    return JsonResponse({'products': products})
