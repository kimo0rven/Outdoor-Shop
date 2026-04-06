from decimal import Decimal
from inventory.models import Listing, ListingVariant

class Cart():
    def __init__(self, request):
        self.session = request.session

        cart = self.session.get('cart')

        if 'cart' not in request.session:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, product, quantity, variant=None):
        product_id = str(product.id)
        variant_id = str(variant.id) if variant else 'None'

        cart_key = f"{product_id}_{variant_id}"

        if cart_key not in self.cart:

            price = str(variant.price) if variant else str(product.base_price)

            self.cart[cart_key] = {
                'product_id': product.id,
                'variant_id': variant.id if variant else None,
                'quantity': int(quantity),
                'price': price,
            }
        else:

            self.cart[cart_key]['quantity'] += int(quantity)

        self.save()

    def update(self, product_id, quantity, variant_id=None):
        product_id = str(product_id)

        variant_id = str(variant_id) if variant_id else 'None'

        cart_key = f"{product_id}_{variant_id}"

        if cart_key in self.cart:
            self.cart[cart_key]['quantity'] = int(quantity)
            self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product_id, variant_id=None):
        product_id = str(product_id)

        variant_id = str(variant_id) if variant_id else 'None'

        cart_key = f"{product_id}_{variant_id}"

        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
            self.save()

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self):
        cart = self.cart.copy()

        for item in cart.values():
            product = Listing.objects.get(id=item['product_id'])
            item['product'] = product

            if item['variant_id']:
                item['variant'] = ListingVariant.objects.get(id=item['variant_id'])
            else:
                item['variant'] = None

            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())