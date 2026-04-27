from decimal import Decimal, InvalidOperation
from products.models import Product, ProductColor


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def _item_key(self, product_id, color_id=None):
        if color_id:
            return f"{product_id}__color_{color_id}"
        return str(product_id)

    def _safe_decimal(self, value):
        """Always returns a proper Decimal, never a string."""
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal('0')

    def add(self, product, quantity=1, override=False, color=None):
        key = self._item_key(product.id, color.id if color else None)
        if key not in self.cart:
            self.cart[key] = {
                'product_id': str(product.id),
                'quantity': 0,
                'price': str(product.effective_price),   # store as string for JSON
                'name': product.name_en,
                'name_ar': product.name_ar,
                'sku': product.sku,
                'color_id': color.id if color else None,
                'color_name': color.name_en if color else None,
                'color_name_ar': color.name_ar if color else None,
                'color_hex': color.hex_code if color else None,
            }
        if override:
            self.cart[key]['quantity'] = int(quantity)
        else:
            self.cart[key]['quantity'] = int(self.cart[key]['quantity']) + int(quantity)

        max_stock = color.stock if color else product.stock
        if self.cart[key]['quantity'] > max_stock:
            self.cart[key]['quantity'] = max_stock

        self.save()

    def remove(self, key):
        key = str(key)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def update(self, key, quantity):
        key = str(key)
        if key in self.cart:
            qty = int(quantity)
            if qty <= 0:
                del self.cart[key]
            else:
                self.cart[key]['quantity'] = qty
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = set(v['product_id'] for v in self.cart.values())
        products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}

        for key, item in self.cart.items():
            item = item.copy()
            item['key'] = key
            item['product'] = products.get(item['product_id'])

            # CRITICAL: always normalize price to clean Decimal string
            # Prevents corrupted session data from causing string concatenation
            price = self._safe_decimal(item['price'])
            qty   = int(item['quantity'])

            # Self-healing: if price looks corrupted (too large), reset from product
            product = item['product']
            if product and (price <= 0 or price > product.effective_price * 20):
                price = product.effective_price
                item['price'] = str(price)  # fix in session copy

            item['price'] = str(price)        # normalize to clean string
            item['total_price'] = price * qty
            yield item

    def __len__(self):
        return sum(int(item['quantity']) for item in self.cart.values())

    def get_total(self):
        total = Decimal('0')
        for item in self.cart.values():
            price = self._safe_decimal(item['price'])
            qty   = int(item['quantity'])
            total += price * qty
        return total

    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
        for key in ['coupon_id', 'coupon_discount']:
            if key in self.session:
                del self.session[key]
        self.session.modified = True
