from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from orders.models import Order
from .models import Payment
import json


def _coming_soon(request, method_name):
    """Show coming soon page for payment methods not yet activated."""
    return render(request, 'payments/coming_soon.html', {'method': method_name})


def paymob_init(request, order_id):
    """Paymob payment — shows coming soon unless API keys are configured."""
    from django.conf import settings
    if not getattr(settings, 'PAYMOB_API_KEY', ''):
        return _coming_soon(request, 'Paymob (Visa/Mastercard)')
    order = get_object_or_404(Order, id=order_id)
    from .providers import get_payment_provider
    provider = get_payment_provider('paymob')
    result = provider.initiate(order)
    if result['success']:
        Payment.objects.get_or_create(order=order, defaults={'provider': 'paymob', 'amount': order.total})
        return redirect(result['redirect_url'])
    messages.error(request, _('Payment initiation failed. Please use Cash on Delivery.'))
    return redirect('orders:checkout')


def fawry_init(request, order_id):
    """Fawry payment — shows coming soon unless merchant keys are configured."""
    from django.conf import settings
    if not getattr(settings, 'FAWRY_MERCHANT_CODE', ''):
        return _coming_soon(request, 'Fawry')
    order = get_object_or_404(Order, id=order_id)
    from .providers import get_payment_provider
    provider = get_payment_provider('fawry')
    result = provider.initiate(order)
    if result['success']:
        payment, _ = Payment.objects.get_or_create(order=order, defaults={'provider': 'fawry', 'amount': order.total})
        payment.provider_reference = result.get('reference_number', '')
        payment.save()
        return render(request, 'payments/fawry_reference.html', {
            'order': order, 'reference': result['reference_number']
        })
    messages.error(request, _('Fawry payment failed. Please use Cash on Delivery.'))
    return redirect('orders:checkout')


@csrf_exempt
def paymob_callback(request):
    data = request.GET if request.method == 'GET' else json.loads(request.body)
    from .providers import get_payment_provider
    provider = get_payment_provider('paymob')
    if provider.verify(data):
        merchant_order_id = data.get('merchant_order_id')
        try:
            order = Order.objects.get(id=merchant_order_id)
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            payment = order.payment
            payment.status = 'success'
            payment.transaction_id = str(data.get('id', ''))
            payment.raw_response = dict(data)
            payment.save()
        except Order.DoesNotExist:
            pass
    return HttpResponse('OK')


@csrf_exempt
def fawry_callback(request):
    data = json.loads(request.body)
    from .providers import get_payment_provider
    provider = get_payment_provider('fawry')
    if provider.verify(data):
        merchant_ref = data.get('merchantRefNum')
        try:
            order = Order.objects.get(id=merchant_ref)
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
        except Order.DoesNotExist:
            pass
    return HttpResponse('OK')
