import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Case, When, Value, IntegerField
from datetime import timedelta
from inventory.models import Listing, Category, Activity, ListingVariant, StockLedger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.db import transaction
from sales.models import Order, Payment
from sales.order_services import create_order_items_and_ledger, line_items_from_session_cart
from accounts.models import ShippingAddress
from .models import PopularSearchTerm
from .cart import Cart
from .forms import ShippingAddressForm
from django.http import JsonResponse
from django.conf import settings

def home_main(request):
    new_threshold = timezone.now() - timedelta(days=30)
    
    new_arrivals = Listing.objects.filter(
        listing_status='active',
        date_created__gte=new_threshold
    ).prefetch_related(
        'variants'
    ).annotate(
        variant_count=Count('variants')
    ).filter(
        variant_count__gt=0
    ).order_by('-date_created')[:12]
    
    if not new_arrivals:
        new_arrivals = Listing.objects.filter(
            listing_status='active'
        ).prefetch_related(
            'variants'
        ).annotate(
            variant_count=Count('variants')
        ).filter(
            variant_count__gt=0
        ).order_by('-date_created')[:8]

    for listing in new_arrivals:
        card_image_url = None
        for variant in listing.variants.all():
            if variant.thumbnail:
                card_image_url = variant.thumbnail.url
                break
        listing.card_image_url = card_image_url

    return render(request, 'OutdoorShop/home.html', {'new_arrivals': new_arrivals})

def product_detail(request, pk):
    product = get_object_or_404(
        Listing.objects.select_related('category', 'activity', 'size_guide')
        .prefetch_related('variants__attributes', 'variants__images'),
        pk=pk
    )
    
    related_products = []
    
    if product.tags:
        tag_list = [tag.strip() for tag in product.tags.split(',') if tag.strip()]
        
        if tag_list:
            tag_query = Q()
            for tag in tag_list:
                tag_query |= Q(tags__icontains=tag)
            
            tagged_products = Listing.objects.filter(
                tag_query,
                listing_status='active'
            ).exclude(pk=pk).distinct()[:4]
            
            related_products = list(tagged_products)
    
    if len(related_products) < 4:
        needed_items = 4 - len(related_products)
        
        existing_ids = [item.id for item in related_products]
        existing_ids.append(product.id)
        
        fallback_products = Listing.objects.filter(
            category=product.category,
            listing_status='active'
        ).exclude(id__in=existing_ids)[:needed_items]

        related_products.extend(list(fallback_products))

    variants = product.variants.all()
    grouped_attributes = {}
    variant_mapping = {}
    variant_gallery_images = []
    default_main_image_url = None

    for variant in variants:
        attrs = variant.attributes.all()
        attr_dict = {attr.name: attr.value for attr in attrs}
        
        for name, value in attr_dict.items():
            if name not in grouped_attributes:
                grouped_attributes[name] = set()
            grouped_attributes[name].add(value)
            
        sorted_keys = sorted(attr_dict.keys())
        combo_key = "|".join([f"{k}:{attr_dict[k]}" for k in sorted_keys])

        variant_image_urls = [
            img.image_file.url
            for img in variant.images.all().order_by('id')
        ]
        main_image_url = (
            variant_image_urls[0]
            if variant_image_urls
            else (variant.thumbnail.url if variant.thumbnail else None)
        )

        if default_main_image_url is None and main_image_url:
            default_main_image_url = main_image_url

        if variant_image_urls:
            variant_gallery_images.extend(variant_image_urls)
        elif variant.thumbnail:
            variant_gallery_images.append(variant.thumbnail.url)
        
        variant_mapping[combo_key] = {
            'id': variant.id,
            'price': str(variant.price),
            'sku': variant.sku,
            'stock': variant.current_stock_quantity,
            'thumbnail': variant.thumbnail.url if variant.thumbnail else None,
            'main_image': main_image_url,
        }
    
    def custom_sort(val):
        size_map = {"XXS": 1, "XS": 2, "S": 3, "M": 4, "L": 5, "XL": 6, "XXL": 7, "XXXL": 8}
        val_upper = str(val).strip().upper()
        
        if val_upper in size_map:
            return (0, size_map[val_upper])
        try:
            import re
            num = float(re.sub(r'[^\d.]', '', str(val)))
            return (1, num)
        except ValueError:
            pass
        return (2, str(val))

    for key in grouped_attributes:
        grouped_attributes[key] = sorted(list(grouped_attributes[key]), key=custom_sort)


    context = {
        'product': product,
        'variants': variants,
        'variant_gallery_images': variant_gallery_images,
        'default_main_image_url': default_main_image_url,
        'related_products': related_products,
        'grouped_attributes': grouped_attributes,
        'variant_mapping_json': json.dumps(variant_mapping),
    }

    return render(request, 'OutdoorShop/product_detail.html', context)

def all_products(request):
    products = Listing.objects.filter(listing_status='active').prefetch_related('variants').annotate(variant_count=Count('variants')).filter(variant_count__gt=0)
    
    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    selected_activities = [int(x) for x in request.GET.getlist('activity') if x.isdigit()]
    selected_genders = request.GET.getlist('gender')
    
    sort_by = request.GET.get('sort', 'newest')

    if selected_categories:
        products = products.filter(category__id__in=selected_categories)
    if selected_brands:
        products = products.filter(brand__in=selected_brands)
    if selected_activities:
        products = products.filter(activity__id__in=selected_activities)
    if selected_genders:
        products = products.filter(gender__in=selected_genders)
    
    if sort_by == 'lowest_price':
        products = products.order_by('base_price')
    elif sort_by == 'highest_price':
        products = products.order_by('-base_price')
    elif sort_by == 'older':
        products = products.order_by('date_created')
    elif sort_by == 'bestseller':
        products = products.order_by('-date_created')
    else:
        products = products.order_by('-date_created')

    context = {
        'products': products,
        'page_title': "All Products",
        'categories': Category.objects.all(),
        'activities': Activity.objects.all(),
        'brands': Listing.objects.filter(listing_status='active').exclude(brand__exact='').values_list('brand', flat=True).distinct(),
        'selected_categories': [int(c) for c in selected_categories if c.isdigit()],
        'selected_brands': selected_brands,
        'selected_activities': selected_activities,
        'selected_genders': selected_genders,
        'current_sort': sort_by,
    }
    
    return render(request, 'OutdoorShop/products_list.html', context)

def search_products(request):
    query = request.GET.get('q', '').strip()
    
    sort_by = request.GET.get('sort', 'newest')
    
    selected_categories = [int(x) for x in request.GET.getlist('category')]
    selected_brands = request.GET.getlist('brand')
    selected_activities = [int(x) for x in request.GET.getlist('activity')]
    selected_genders = request.GET.getlist('gender')

    products = Listing.objects.filter(listing_status='active').prefetch_related('variants').annotate(variant_count=Count('variants')).filter(variant_count__gt=0)

    if query:
        PopularSearchTerm.record(query)
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(tags__icontains=query) |
            Q(category__category_name__icontains=query)
        ).distinct()

    if selected_categories:
        products = products.filter(category__id__in=selected_categories)
        
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    if selected_activities:
        products = products.filter(activity__id__in=selected_activities)

    if selected_genders:
        products = products.filter(gender__in=selected_genders)

    if sort_by == 'lowest_price':
        products = products.order_by('base_price')
    elif sort_by == 'highest_price':
        products = products.order_by('-base_price')
    elif sort_by == 'older':
        products = products.order_by('date_created')
    elif sort_by == 'bestseller':
        products = products.order_by('-date_created')
    else: 
        products = products.order_by('-date_created')

    categories = Category.objects.all()
    activities = Activity.objects.all()
    brands = Listing.objects.filter(listing_status='active').exclude(brand__exact='').values_list('brand', flat=True).distinct()

    context = {
        'products': products,
        'page_title': f"Search Results for '{query}'" if query else "All Products",
        'search_query': query,
        'categories': categories,
        'activities': activities,
        'brands': brands,
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
        'selected_activities': selected_activities,
        'selected_genders': selected_genders,
        'current_sort': sort_by,
    }
    
    return render(request, 'OutdoorShop/products_list.html', context)

def cart_add(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))

        if variant_id:
            variant = get_object_or_404(ListingVariant, id=variant_id)
            product = variant.listing
            cart.add(product=product, quantity=quantity, variant=variant)
            messages.success(request, f"Added {quantity}x {product.name} to your cart.")
        
        elif product_id:
            product = get_object_or_404(Listing, id=product_id)
            cart.add(product=product, quantity=quantity)
            messages.success(request, f"Added {quantity}x {product.name} to your cart.")

        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')

def cart_remove(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')
        
        cart.remove(product_id=product_id, variant_id=variant_id)
        messages.success(request, "Item removed from your cart.")
        
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'OutdoorShop/cart.html', {'cart': cart})

@login_required 
def checkout(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        return redirect('cart_detail')
        
    addresses = request.user.shipping_addresses.all().order_by('-is_default', '-id')
    saved_address = addresses.first()
            
    context = {
        'cart': cart,
        'total_amount': cart.get_total_price(),
        'saved_address': saved_address,
        'addresses': addresses,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    }
    return render(request, 'OutdoorShop/checkout.html', context)

@login_required
def save_address(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            with transaction.atomic():
                ShippingAddress.objects.filter(user=request.user).update(is_default=False)
                address = ShippingAddress.objects.create(
                    user=request.user,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    phone_number=data.get('phone_number', ''),
                    address_line_1=data.get('address_line_1', ''),
                    address_line_2=data.get('address_line_2', ''),
                    city=data.get('city', ''),
                    state=data.get('state', ''),
                    postal_code=data.get('postal_code', ''),
                    country='Philippines',
                    is_default=True,
                )
            return JsonResponse({'status': 'success', 'address_id': address.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def process_order(request):
    if request.method == 'POST':
        cart = Cart(request)
        try:
            data = json.loads(request.body)
            shipping = data.get('shipping')
            transaction_id = data.get('paypal_transaction_id')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'status': 'error', 'message': 'Invalid data received.'})

        if not shipping or not transaction_id:
            return JsonResponse({'status': 'error', 'message': 'Missing shipping or transaction info.'})

        try:
            with transaction.atomic():
                address, created = ShippingAddress.objects.update_or_create(
                    user=request.user,
                    first_name=shipping['first_name'],
                    last_name=shipping['last_name'],
                    address_line_1=shipping['address_1'],
                    city=shipping['city'],
                    defaults={
                        'address_line_2': shipping.get('address_2'),
                        'state': shipping['state'],
                        'postal_code': shipping['zipcode'],
                        'phone_number': shipping['phone'],
                        'is_default': True
                    }
                )

                order = Order.objects.create(
                    user=request.user,
                    total_amount=cart.get_total_price(),
                    status='processing',
                    order_source=Order.SOURCE_WEB,
                    shipping_address=address
                )

                Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    method='card',
                    transaction_id=transaction_id,
                    payment_status='Completed'
                )

                lines = line_items_from_session_cart(cart)
                create_order_items_and_ledger(
                    order,
                    lines,
                    order_source=Order.SOURCE_WEB,
                    staff_user=None,
                    paypal_txn_id=transaction_id,
                )

                cart.clear()
                
                return JsonResponse({
                    'status': 'success', 
                    'order_id': order.id,
                    'message': 'Order and Payment processed successfully.'
                })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def order_history(request):
    status_ordering = Case(
        When(status='pending', then=Value(1)),
        When(status='processing', then=Value(2)),
        When(status='shipped', then=Value(3)),
        When(status='delivered', then=Value(4)),
        When(status='cancelled', then=Value(5)),
        default=Value(6),
        output_field=IntegerField(),
    )
    orders = Order.objects.filter(user=request.user).annotate(
        priority=status_ordering
    ).order_by('priority', '-order_date').prefetch_related('items__listing_variant__listing')
    
    context = {
        'orders': orders,
        'page_title': 'My Order History'
    }
    return render(request, 'OutdoorShop/order_history.html', context)

@login_required
def profile(request):
    shipping_addresses = request.user.shipping_addresses.all().order_by(
        '-is_default',
        '-date_created',
        '-id',
    )

    default_address = shipping_addresses.first()
    orders_count = Order.objects.filter(user=request.user).count()

    password_form = PasswordChangeForm(user=request.user)
    if request.method == 'POST' and request.POST.get('action') == 'change_password':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated.')
            return redirect('profile')
        messages.error(request, 'Please correct the errors below.')

    context = {
        'page_title': 'My Profile',
        'shipping_addresses': shipping_addresses,
        'default_address': default_address,
        'orders_count': orders_count,
        'password_form': password_form,
    }
    return render(request, 'OutdoorShop/profile.html', context)

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        ShippingAddress.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
        address.save(update_fields=['is_default'])
        messages.success(request, 'Default shipping address updated.')

    redirect_url = request.META.get('HTTP_REFERER') or reverse('profile')
    return redirect(redirect_url)


@login_required
def address_book(request):
    shipping_addresses = request.user.shipping_addresses.all().order_by(
        '-is_default',
        '-date_created',
        '-id',
    )
    context = {
        'page_title': 'Address Book',
        'shipping_addresses': shipping_addresses,
    }
    return render(request, 'OutdoorShop/address_book.html', context)


@login_required
def address_create(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_default:
                ShippingAddress.objects.filter(user=request.user).update(is_default=False)

            address.save()
            messages.success(request, 'Shipping address added.')
            return redirect('address_book')
    else:
        form = ShippingAddressForm()

    context = {
        'page_title': 'Add Shipping Address',
        'form': form,
    }
    return render(request, 'OutdoorShop/address_form.html', context)


@login_required
def address_edit(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            updated = form.save(commit=False)

            if updated.is_default:
                ShippingAddress.objects.filter(user=request.user).exclude(id=updated.id).update(is_default=False)

            updated.save()
            messages.success(request, 'Shipping address updated.')
            return redirect('address_book')
    else:
        form = ShippingAddressForm(instance=address)

    context = {
        'page_title': 'Edit Shipping Address',
        'form': form,
        'address': address,
    }
    return render(request, 'OutdoorShop/address_form.html', context)

@login_required
def address_delete(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        if address.is_default:
            messages.error(request, 'Cannot delete default address. Please set another address as default first.')
            return redirect('address_book')

        address.delete()
        messages.success(request, 'Shipping address deleted.')

    redirect_url = request.META.get('HTTP_REFERER') or reverse('address_book')
    return redirect(redirect_url)

def cart_update(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')
        
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        if quantity <= 0:
            cart.remove(product_id=product_id, variant_id=variant_id)
        else:
            cart.update(product_id=product_id, quantity=quantity, variant_id=variant_id)

    return redirect('cart_detail')

def order_success(request):
    return render(request, 'OutdoorShop/order_success.html')

def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status == 'cancelled' and order.status in ['pending', 'processing']:
                with transaction.atomic():
                    order.status = 'cancelled'
                    order.save()

                    for item in order.items.all():
                        variant = ListingVariant.objects.select_for_update().get(id=item.listing_variant.id)
                        previous_stock = variant.current_stock_quantity

                        variant.current_stock_quantity += item.quantity
                        variant.save()
                        
                        StockLedger.objects.create(
                            variant=variant,
                            transaction_type='adjustment', 
                            quantity_changed=item.quantity, 
                            previous_stock=previous_stock,
                            new_stock=variant.current_stock_quantity,
                            reference_note=f"Restock from Cancelled Order #{order.id}"
                        )
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Order has been cancelled and stock restored.'
                })

            elif new_status == 'delivered' and order.status == 'shipped':
                order.status = 'delivered'
                order.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Thank you! Enjoy your gear.'
                })
                
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'You cannot perform this action right now.'
                })
                
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})