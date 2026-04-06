from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from AginodOutdoorShop.decorators import staff_api_required, staff_member_required
from django.db.models import Q
from inventory.models import ListingVariant, Category, Listing
from .models import Order
from .order_services import complete_pos_checkout
import json

@staff_member_required
def pos_home(request):
    categories = Category.objects.all()
    listings = Listing.objects.filter(
        variants__current_stock_quantity__gt=0
    ).distinct().select_related('category')[:60]
    
    context = {
        'categories': categories,
        'listings': listings,
    }
    return render(request, 'sales/pos.html', context)

@staff_api_required
def pos_get_variants(request, listing_id):
    variants = ListingVariant.objects.filter(
        listing_id=listing_id,
        current_stock_quantity__gt=0,
    ).select_related('listing').prefetch_related('attributes')

    data = []
    for x in variants:
        attrs = list(x.attributes.all())
        attribute_list = [{'name': a.name, 'value': a.value} for a in attrs]
        attribute_string = ' • '.join(
            f'{a.name}: {a.value}' for a in attrs
        )

        data.append({
            'id': x.id,
            'name': x.listing.name,
            'variant_name': x.variant_name,
            'sku': x.sku,
            'price': float(x.price),
            'stock': x.current_stock_quantity,
            'attributes': attribute_string,
            'attribute_list': attribute_list,
        })

    return JsonResponse({'variants': data})

@staff_api_required
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

@staff_api_required
def process_checkout(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        cart_items = data.get('cart', [])
        source = (data.get('source') or '').strip().upper()

        if source != Order.SOURCE_POS:
            return JsonResponse({'success': False, 'message': 'Invalid source'}, status=400)

        if not cart_items:
            return JsonResponse({'success': False, 'message': 'Cart is empty'}, status=400)

        order = complete_pos_checkout(request.user, cart_items)

        return JsonResponse({
            'success': True,
            'message': 'Transaction completed successfully!',
            'order_id': order.id,
        })

    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Internal Server Error'}, status=500)

@staff_member_required
def sales_order(request):
    orders = (
        Order.objects.all()
        .select_related('processed_by', 'user')
        .order_by('-order_date')
    )
    return render(request, 'sales/orders.html', {'orders': orders})


@staff_member_required
def sales_order_detail(request, order_id: int):
    order = get_object_or_404(
        Order.objects
        .select_related('processed_by', 'user', 'payment')
        .prefetch_related('items__listing_variant__listing'),
        id=order_id,
    )
    items = order.items.all()
    return render(request, 'sales/order_detail.html', {'order': order, 'items': items})


@staff_member_required
def sales_order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method != 'POST':
        return redirect('sales:sales_order_detail', order_id=order.id)

    new_status = (request.POST.get('status') or '').strip()
    allowed_statuses = {s for s, _ in Order.STATUS_CHOICES}

    if new_status not in allowed_statuses:
        return redirect('sales:sales_order_detail', order_id=order.id)

    order.status = new_status
    order.processed_by = request.user
    order.save(update_fields=['status', 'processed_by'])

    return redirect('sales:sales_order_detail', order_id=order.id)

