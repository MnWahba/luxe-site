from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from .models import Review
from products.models import Product
from orders.models import OrderItem


@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status='delivered',
        product=product
    ).exists()
    if not has_purchased:
        messages.error(request, _('Only verified buyers can leave a review.'))
        return redirect('products:detail', slug=product.slug)
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, _('You have already reviewed this product.'))
        return redirect('products:detail', slug=product.slug)
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()
    if not comment:
        messages.error(request, _('Please write a comment.'))
        return redirect('products:detail', slug=product.slug)
    Review.objects.create(product=product, user=request.user, rating=rating, comment=comment, is_verified_purchase=True)
    messages.success(request, _('Review submitted! It will be visible after approval.'))
    return redirect('products:detail', slug=product.slug)
