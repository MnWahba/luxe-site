from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from luxe_bags_project.language_view import switch_language
import products.views as pv

# Language switcher OUTSIDE i18n_patterns
from core import urls as core_urls
urlpatterns = [
    path('i18n/setlang/', switch_language, name='set_language'),
    path('', __import__('django.urls',fromlist=['include']).include('core.urls')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', pv.HomeView.as_view(), name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('products/', include('products.urls', namespace='products')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('coupons/', include('coupons.urls', namespace='coupons')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
