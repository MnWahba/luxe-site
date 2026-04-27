from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<uuid:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<uuid:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<uuid:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('detail/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
