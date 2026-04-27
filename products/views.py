from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Avg
from .models import Product, Category, ProductImage, Wishlist


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['featured_products'] = Product.objects.filter(is_active=True, is_featured=True)[:8]
        ctx['new_arrivals'] = Product.objects.filter(is_active=True, is_new_arrival=True)[:8]
        ctx['categories'] = Category.objects.filter(is_active=True)[:6]
        ctx['bestsellers'] = Product.objects.filter(is_active=True).order_by('-views_count')[:4]
        # Site settings (hero, promo, stats) — editable from Admin
        from core.models import SiteSettings
        ctx['site'] = SiteSettings.get()
        # Real stats
        from orders.models import OrderItem
        from django.db.models import Sum as _Sum
        ctx['stat_products_count'] = Product.objects.filter(is_active=True).count()
        return ctx


class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        cat_slug = self.kwargs.get('category_slug')
        if cat_slug:
            qs = qs.filter(category__slug=cat_slug)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name_en__icontains=q) | Q(name_ar__icontains=q) | Q(description_en__icontains=q))
        sort = self.request.GET.get('sort', '-created_at')
        sort_map = {
            'price_asc': 'price', 'price_desc': '-price',
            'newest': '-created_at', 'popular': '-views_count',
        }
        qs = qs.order_by(sort_map.get(sort, '-created_at'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cat_slug = self.kwargs.get('category_slug')
        if cat_slug:
            ctx['current_category'] = get_object_or_404(Category, slug=cat_slug)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['sort'] = self.request.GET.get('sort', 'newest')
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'

    def get_object(self):
        obj = super().get_object()
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['related_products'] = Product.objects.filter(
            category=self.object.category, is_active=True
        ).exclude(pk=self.object.pk)[:4]
        ctx['reviews'] = self.object.reviews.filter(is_approved=True).order_by('-created_at')
        if self.request.user.is_authenticated:
            ctx['in_wishlist'] = Wishlist.objects.filter(user=self.request.user, product=self.object).exists()
            from orders.models import Order, OrderItem
            ctx['can_review'] = OrderItem.objects.filter(
                order__user=self.request.user,
                order__status__in=['delivered'],
                product=self.object
            ).exists() and not self.object.reviews.filter(user=self.request.user).exists()
        return ctx


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        in_wishlist = False
        msg = _('Removed from wishlist')
    else:
        in_wishlist = True
        msg = _('Added to wishlist')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist, 'message': str(msg)})
    messages.success(request, msg)
    return redirect('products:detail', slug=product.slug)


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'items': items})


def search_view(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True).filter(
        Q(name_en__icontains=q) | Q(name_ar__icontains=q)
    ) if q else Product.objects.none()
    return render(request, 'products/search.html', {'products': products, 'query': q})
