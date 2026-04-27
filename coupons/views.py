from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from .models import Coupon
from orders.cart import Cart
import json


@require_POST
def apply_coupon(request):
    data = json.loads(request.body)
    code = data.get('code', '').strip().upper()
    cart = Cart(request)
    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid:
            return JsonResponse({'success': False, 'error': str(_('This coupon is expired or invalid.'))})
        cart_total = cart.get_total()
        if cart_total < coupon.minimum_order:
            return JsonResponse({'success': False, 'error': str(_(f'Minimum order is {coupon.minimum_order} EGP'))})
        discount = coupon.calculate_discount(cart_total)
        request.session['coupon_id'] = coupon.id
        request.session['coupon_discount'] = float(discount)
        return JsonResponse({
            'success': True,
            'discount': float(discount),
            'new_total': float(cart_total - discount),
            'message': str(_(f'Coupon applied! You save {discount:.0f} EGP'))
        })
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'error': str(_('Invalid coupon code.'))})


def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']
    return JsonResponse({'success': True})
