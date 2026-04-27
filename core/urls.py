from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('admin/core/sales/', views.sales_report_view, name='sales_report'),
    path('admin/core/kpis/', views.kpis_api, name='kpis_api'),
    path('admin/core/sales-data/', views.sales_data_api, name='sales_data_api'),
    path('admin/core/recent-orders/', views.recent_orders_api, name='recent_orders_api'),
    path('admin/core/low-stock/', views.low_stock_api, name='low_stock_api'),
]
