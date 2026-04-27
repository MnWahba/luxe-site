from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('reset-password/<uuid:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/', views.profile_view, name='profile'),
    path('address/add/', views.add_address_view, name='add_address'),
    path('address/delete/<int:pk>/', views.delete_address_view, name='delete_address'),
    path('locked/', views.locked_out_view, name='locked_out'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('send-reset-email/', views.send_password_reset_by_email, name='send_reset_email'),
]
