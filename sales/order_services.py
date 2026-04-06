from decimal import Decimal

from django.db import transaction

from inventory.models import ListingVariant, StockLedger
from sales.models import Order, OrderItem, Payment


def line_items_from_session_cart(cart):
    lines = []
    for item in cart:
        lines.append(
            {
                'variant_id': item['variant'].id,
                'quantity': int(item['quantity']),
                'unit_price': item['price'],
            }
        )
    return lines


def compute_total_from_lines(lines):
    return sum(Decimal(str(line['unit_price'])) * int(line['quantity']) for line in lines)


def _ledger_reference(order, *, order_source, paypal_txn_id=None):
    if order_source == Order.SOURCE_WEB:
        return f"Online Order #{order.id} | PayPal TXN: {paypal_txn_id or ''}"
    return f"POS Order #{order.id} | Staff sale"


def create_order_items_and_ledger(
    order,
    lines,
    *,
    order_source,
    staff_user,
    paypal_txn_id=None,
):
    for line in lines:
        variant = ListingVariant.objects.select_for_update().get(id=line['variant_id'])
        qty = int(line['quantity'])
        unit_price = Decimal(str(line['unit_price']))

        if variant.current_stock_quantity < qty:
            raise ValueError(f"Insufficient stock for {variant.listing.name}.")

        previous_stock = variant.current_stock_quantity
        variant.current_stock_quantity -= qty
        variant.save()

        OrderItem.objects.create(
            order=order,
            listing_variant=variant,
            quantity=qty,
            price=unit_price,
        )

        StockLedger.objects.create(
            variant=variant,
            staff=staff_user if order_source == Order.SOURCE_POS else None,
            transaction_type='sale',
            quantity_changed=-qty,
            previous_stock=previous_stock,
            new_stock=variant.current_stock_quantity,
            reference_note=_ledger_reference(
                order, order_source=order_source, paypal_txn_id=paypal_txn_id
            ),
        )


def complete_pos_checkout(staff_user, cart_items):
    if not cart_items:
        raise ValueError('Cart is empty')

    with transaction.atomic():
        lines = []
        for raw in cart_items:
            vid = int(raw['id'])
            qty = int(raw['qty'])
            variant = ListingVariant.objects.get(id=vid)
            lines.append(
                {
                    'variant_id': vid,
                    'quantity': qty,
                    'unit_price': variant.price,
                }
            )

        total = compute_total_from_lines(lines)

        order = Order.objects.create(
            user=None,
            processed_by=staff_user,
            total_amount=total,
            status='completed',
            order_source=Order.SOURCE_POS,
            shipping_address=None,
        )

        Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method='cash',
            transaction_id='',
            payment_status='Completed',
        )

        create_order_items_and_ledger(
            order,
            lines,
            order_source=Order.SOURCE_POS,
            staff_user=staff_user,
            paypal_txn_id=None,
        )

    return order
