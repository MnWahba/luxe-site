from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('paymob/init/<uuid:order_id>/', views.paymob_init, name='paymob_init'),
    path('fawry/init/<uuid:order_id>/', views.fawry_init, name='fawry_init'),
    path('paymob/callback/', views.paymob_callback, name='paymob_callback'),
    path('fawry/callback/', views.fawry_callback, name='fawry_callback'),
]
