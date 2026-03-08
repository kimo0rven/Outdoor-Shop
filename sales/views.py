from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from inventory.models import ListingVariant, Category, StockLedger
from .models import Order, OrderItem, Payment
import json

@login_required
def pos_home(request):
    categories = Category.objects.all()
    return render(request, 'sales/pos.html', {'categories': categories})

@login_required
def pos_search_products(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    products = ListingVariant.objects.filter(
        Q(sku__icontains=query) | 
        Q(listing__name__icontains=query) |
        Q(variant_name__icontains=query),
        current_stock_quantity__gt=0
    ).select_related('listing')[:10]

    results = []
    for p in products:
        image_url = ''
        first_img = p.images.first()
        if first_img:
            image_url = first_img.image_file.url
        elif p.listing.thumbnail:
            image_url = p.listing.thumbnail.url

        results.append({
            'id': p.id,
            'name': f"{p.listing.name} ({p.variant_name})",
            'price': float(p.price),
            'stock': p.current_stock_quantity,
            'sku': p.sku,
            'image': image_url
        })
    return JsonResponse({'results': results})

@login_required
@transaction.atomic
def process_checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("DEBUG RECEIVED DATA:", data)
            cart_items = data.get('cart', [])
            order_source = data.get('source', Order.SOURCE_WEB)
            
            if not cart_items:
                return JsonResponse({'success': False, 'message': 'Cart is empty'}, status=400)

            new_order = Order.objects.create(
                user=request.user if order_source == Order.SOURCE_WEB else None,
                processed_by=request.user if order_source == Order.SOURCE_POS else None,
                total_amount=data.get('total'),
                status='completed' if order_source == Order.SOURCE_POS else 'pending',
                order_source=order_source
            )

            for item in cart_items:
                variant = ListingVariant.objects.select_for_update().get(id=item['id'])

                if variant.current_stock_quantity < item['qty']:
                    raise ValueError(f"Insufficient stock for {variant.sku}. Available: {variant.current_stock_quantity}")

                unit_price = float(item['price'])
                qty = int(item['qty'])
                OrderItem.objects.create(
                    order=new_order,
                    listing_variant=variant,
                    quantity=qty,
                    price=unit_price,
                    item_total=unit_price * qty
                )

                old_stock = variant.current_stock_quantity
                variant.current_stock_quantity -= qty
                if variant.current_stock_quantity == 0:
                    variant.status = 'out_of_stock'
                variant.save()

                StockLedger.objects.create(
                    variant=variant,
                    staff=request.user if order_source == Order.SOURCE_POS else None,
                    transaction_type='sale',
                    quantity_changed=-qty,
                    previous_stock=old_stock,
                    new_stock=variant.current_stock_quantity,
                    reference_note=f"Order #{new_order.id} ({order_source})"
                )

            Payment.objects.create(
                order=new_order,
                amount=data.get('total'),
                method=data.get('payment_method', 'Cash'),
                transaction_id=data.get('transaction_id', ''),
                payment_status='paid' if order_source == Order.SOURCE_POS else 'pending'
            )

            return JsonResponse({
                'success': True, 
                'message': 'Transaction completed successfully!',
                'order_id': new_order.id
            })

        except ValueError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Internal Server Error'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'sales/orders.html', {'orders': orders})