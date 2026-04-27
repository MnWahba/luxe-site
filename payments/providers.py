"""
Payment Provider Abstraction Layer
Ready for Paymob and Fawry integration
"""
import hashlib
import hmac
import json
import requests
from django.conf import settings


class BasePaymentProvider:
    def initiate(self, order): raise NotImplementedError
    def verify(self, data): raise NotImplementedError
    def refund(self, transaction_id, amount): raise NotImplementedError


class PaymobProvider(BasePaymentProvider):
    """
    Paymob integration - https://developers.paymob.com/
    Steps: 1) Auth token  2) Create order  3) Payment key  4) Redirect to iframe
    """
    BASE_URL = 'https://accept.paymobsolutions.com/api'

    def _get_auth_token(self):
        r = requests.post(f'{self.BASE_URL}/auth/tokens', json={'api_key': settings.PAYMOB_API_KEY})
        return r.json().get('token')

    def _create_order(self, token, order):
        r = requests.post(f'{self.BASE_URL}/ecommerce/orders', json={
            'auth_token': token,
            'delivery_needed': False,
            'amount_cents': int(order.total * 100),
            'currency': 'EGP',
            'merchant_order_id': str(order.id),
            'items': [{'name': i.product_name, 'amount_cents': int(i.price * 100), 'description': i.product_name, 'quantity': i.quantity} for i in order.items.all()],
        })
        return r.json().get('id')

    def _get_payment_key(self, token, paymob_order_id, order):
        billing = {
            'apartment': 'NA', 'email': order.email, 'floor': 'NA',
            'first_name': order.full_name.split()[0], 'street': order.address_line1,
            'building': 'NA', 'phone_number': order.phone, 'shipping_method': 'NA',
            'postal_code': 'NA', 'city': order.city, 'country': 'EGY',
            'last_name': order.full_name.split()[-1], 'state': order.governorate,
        }
        r = requests.post(f'{self.BASE_URL}/acceptance/payment_keys', json={
            'auth_token': token,
            'amount_cents': int(order.total * 100),
            'expiration': 3600,
            'order_id': paymob_order_id,
            'billing_data': billing,
            'currency': 'EGP',
            'integration_id': settings.PAYMOB_INTEGRATION_ID,
        })
        return r.json().get('token')

    def initiate(self, order):
        try:
            token = self._get_auth_token()
            paymob_order_id = self._create_order(token, order)
            payment_key = self._get_payment_key(token, paymob_order_id, order)
            iframe_url = f'https://accept.paymobsolutions.com/api/acceptance/iframes/{settings.PAYMOB_INTEGRATION_ID}?payment_token={payment_key}'
            return {'success': True, 'redirect_url': iframe_url, 'payment_key': payment_key}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verify(self, data):
        """Verify Paymob HMAC callback"""
        received_hmac = data.get('hmac')
        fields = ['amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction',
                  'id', 'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded',
                  'is_standalone_payment', 'is_voided', 'order', 'owner', 'pending', 'source_data.pan',
                  'source_data.sub_type', 'source_data.type', 'success']
        values = ''.join(str(data.get(f, '')) for f in fields)
        expected = hmac.new(settings.PAYMOB_HMAC_SECRET.encode(), values.encode(), hashlib.sha512).hexdigest()
        return received_hmac == expected and data.get('success') == 'true'

    def refund(self, transaction_id, amount):
        try:
            token = self._get_auth_token()
            r = requests.post(f'{self.BASE_URL}/acceptance/void_refund/refund', json={
                'auth_token': token, 'transaction_id': transaction_id,
                'amount_cents': int(amount * 100),
            })
            return r.json().get('success', False)
        except Exception:
            return False


class FawryProvider(BasePaymentProvider):
    """
    Fawry integration - https://developer.fawry.com/
    """
    BASE_URL = 'https://www.atfawry.com/ECommerceWeb/Fawry/payments'

    def _generate_signature(self, merchant_code, merchant_ref, expiry, items, security_key):
        items_str = ''.join(f"{i['itemId']}{i['quantity']}{i['price']}" for i in items)
        raw = f"{merchant_code}{merchant_ref}{expiry}{items_str}{security_key}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def initiate(self, order):
        try:
            items = [{'itemId': str(i.product_id), 'description': i.product_name,
                      'price': float(i.price), 'quantity': i.quantity} for i in order.items.all()]
            sig = self._generate_signature(
                settings.FAWRY_MERCHANT_CODE, str(order.id), '20160516', items, settings.FAWRY_SECURITY_KEY
            )
            payload = {
                'merchantCode': settings.FAWRY_MERCHANT_CODE,
                'merchantRefNum': str(order.id),
                'customerMobile': order.phone,
                'customerEmail': order.email,
                'paymentExpiry': '20991231',
                'chargeItems': items,
                'signature': sig,
                'paymentMethod': 'PayAtFawry',
                'returnUrl': f'https://yourdomain.com/payments/fawry/callback/',
            }
            r = requests.post(f'{self.BASE_URL}/charge', json=payload)
            result = r.json()
            if result.get('type') == 'ChargeResponse':
                return {'success': True, 'reference_number': result.get('referenceNumber')}
            return {'success': False, 'error': result.get('description', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verify(self, data):
        return data.get('paymentStatus') == 'PAID'

    def refund(self, transaction_id, amount):
        return False


def get_payment_provider(method):
    providers = {
        'paymob': PaymobProvider(),
        'fawry': FawryProvider(),
    }
    return providers.get(method)
