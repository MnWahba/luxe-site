from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.http import require_POST
from .cart import Cart
from .models import Order, OrderItem
from products.models import Product
from coupons.models import Coupon
import json


def cart_view(request):
    cart = Cart(request)
    from decimal import Decimal as _D
    coupon_discount = _D(str(request.session.get('coupon_discount', 0)))
    total = cart.get_total()
    final_total = total - coupon_discount
    return render(request, 'orders/cart.html', {
        'cart': cart,
        'subtotal': total,
        'coupon_discount': coupon_discount,
        'final_total': final_total,
    })


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    color_id = request.POST.get('color_id') or None
    color = None

    if color_id:
        from products.models import ProductColor
        try:
            color = ProductColor.objects.get(id=color_id, product=product, is_active=True)
            if color.stock <= 0:
                err = _('This color is out of stock.')
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': str(err)})
                messages.error(request, err)
                return redirect('products:detail', slug=product.slug)
        except ProductColor.DoesNotExist:
            color = None

    # If product has colors but none selected, require selection
    if not color and product.colors.filter(is_active=True).exists():
        err = _('Please select a color.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(err)})
        messages.error(request, err)
        return redirect('products:detail', slug=product.slug)

    cart.add(product, quantity, color=color)
    color_label = f' ({color.name_en})' if color else ''

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': len(cart), 'message': str(_('Added to cart!')) + color_label})
    messages.success(request, _(f'Added to cart!') + color_label)
    return redirect('orders:cart')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    key = request.POST.get('cart_key', str(product_id))
    cart.update(key, quantity)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': len(cart)})
    return redirect('orders:cart')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    key = request.POST.get('cart_key', str(product_id))
    cart.remove(key)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': len(cart)})
    return redirect('orders:cart')


def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, _('Your cart is empty.'))
        return redirect('orders:cart')

    from decimal import Decimal
    coupon_discount = Decimal(str(request.session.get('coupon_discount', 0)))
    subtotal = cart.get_total()
    total = subtotal - coupon_discount

    initial = {}
    if request.user.is_authenticated:
        initial = {
            'full_name': request.user.full_name,
            'email': request.user.email,
            'phone': request.user.phone,
        }
        default_addr = request.user.addresses.filter(is_default=True).first()
        if default_addr:
            initial.update({
                'address_line1': default_addr.address_line1,
                'address_line2': default_addr.address_line2,
                'city': default_addr.city,
                'governorate': default_addr.governorate,
            })

    if request.method == 'POST':
        # Validate stock
        for item in cart:
            product = item.get('product')
            if product and item['quantity'] > product.stock:
                messages.error(request, _(f'Not enough stock for {product.name_en}'))
                return redirect('orders:cart')

        coupon = None
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
            except Coupon.DoesNotExist:
                pass

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address_line1=request.POST.get('address_line1'),
            address_line2=request.POST.get('address_line2', ''),
            city=request.POST.get('city'),
            governorate=request.POST.get('governorate'),
            subtotal=subtotal,
            discount=coupon_discount,
            total=total,
            coupon=coupon,
            payment_method=request.POST.get('payment_method', 'cod'),
            notes=request.POST.get('notes', ''),
        )

        for item in cart:
            product = item.get('product')
            if product:
                img = product.get_primary_image()
                # Color info
                color_info = ''
                if item.get('color_name'):
                    color_info = f" [{item['color_name']}]"
                    # Use color image if available
                    if item.get('color_id'):
                        from products.models import ProductColor as PC
                        try:
                            pc = PC.objects.get(id=item['color_id'])
                            if pc.image:
                                img = pc  # use color image
                        except PC.DoesNotExist:
                            pass

                # Always use current product price (sanitised, prevents session corruption)
                try:
                    safe_price = Decimal(str(item['price']))
                    # Sanity check: price shouldn't be more than 10x product price
                    if safe_price > product.effective_price * 20 or safe_price <= 0:
                        safe_price = product.effective_price
                except Exception:
                    safe_price = product.effective_price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name_en + color_info,
                    product_sku=product.sku,
                    price=safe_price,
                    quantity=int(item['quantity']),
                    image_url=img.image.url if img else '',
                )
                product.stock -= item['quantity']
                product.save(update_fields=['stock'])

        if coupon:
            coupon.usage_count += 1
            coupon.save(update_fields=['usage_count'])

        # Send confirmation email
        try:
            msg = render_to_string('orders/emails/order_confirmation.html', {
                'order': order, 'store_name': settings.STORE_NAME
            })
            send_mail(
                f'Order Confirmed #{order.order_number}',
                msg, settings.DEFAULT_FROM_EMAIL,
                [order.email], html_message=msg, fail_silently=True
            )
        except Exception:
            pass

        cart.clear()
        payment_method = order.payment_method

        if payment_method == 'cod':
            return redirect('orders:order_success', order_number=order.order_number)
        elif payment_method == 'paymob':
            return redirect('payments:paymob_init', order_id=order.id)
        elif payment_method == 'fawry':
            return redirect('payments:fawry_init', order_id=order.id)

    GOVERNORATES = [
        'Cairo', 'Giza', 'Alexandria', 'Dakahlia', 'Red Sea', 'Beheira',
        'Fayoum', 'Gharbiya', 'Ismailia', 'Menofia', 'Minya', 'Qalyubia',
        'New Valley', 'North Sinai', 'Port Said', 'Sharqia', 'South Sinai',
        'Suez', 'Luxor', 'Matruh', 'Qena', 'Aswan', 'Assiut', 'Beni Suef',
        'Kafr Al sheikh', 'Damietta', 'Sohag',
    ]

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'subtotal': subtotal,
        'coupon_discount': coupon_discount,
        'total': total,
        'initial': initial,
        'governorates': GOVERNORATES,
    })


def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


def context_processors_import():
    pass


def cart_clear(request):
    """Clear the entire cart — useful when session data is corrupted."""
    cart = Cart(request)
    cart.clear()
    messages.success(request, _('Cart cleared.'))
    return redirect('orders:cart')
