from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ListingVariant, Listing, ListingImage, Category, ProductAttribute, StockLedger, Activity, ListingGalleryImage

@login_required(login_url='login')
def inventory_units(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        variant_name = request.POST.get('variant_name')
        sku = request.POST.get('sku')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        status = request.POST.get('status', 'in_stock')
        
        parent_listing = Listing.objects.get(id=listing_id)
        
        variant_images = request.FILES.getlist('variant_images')
        first_image = variant_images[0] if variant_images else None

        variant = ListingVariant.objects.create(
            listing=parent_listing,
            sku=sku,
            variant_name=variant_name,
            price=price,
            current_stock_quantity=quantity,
            status=status,
            thumbnail=first_image
        )
        
        for img in variant_images:
            ListingImage.objects.create(
                listing_variant=variant,
                image_file=img
            )

        names = request.POST.getlist('attr_name[]')
        values = request.POST.getlist('attr_val[]')
        for name, value in zip(names, values):
            if name.strip() and value.strip():
                ProductAttribute.objects.create(variant=variant, name=name, value=value)
        
        messages.success(request, f"Variant {sku} created successfully!")
        return redirect('units')

    variants = ListingVariant.objects.select_related('listing__category').prefetch_related('attributes', 'images').all()
    listings = Listing.objects.all()
    return render(request, 'inventory/units.html', {'variants': variants, 'listings': listings})


@login_required(login_url='login')
def edit_variant(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        variant = get_object_or_404(ListingVariant, id=variant_id)
        variant_name = request.POST.get('variant_name')
        qty_raw = request.POST.get('quantity', 0)
        sku = request.POST.get('sku')
        price = request.POST.get('price')
        qty = int(request.POST.get('quantity', 0))
        status = request.POST.get('status', 'in_stock')
        
        
        if not sku or not price:
            messages.error(request, "SKU and Price are required.")
            return redirect('units')

        if qty > 0 and status == 'out_of_stock':
            status = 'in_stock'

        elif qty <= 0:
            status = 'out_of_stock'

        variant.variant_name = variant_name
        variant.current_stock_quantity = int(qty_raw)
        variant.sku = sku
        variant.price = price
        variant.quantity = qty
        variant.status = status
        variant.save()
        
        new_photo = request.FILES.get('variant_image')
        if new_photo:
            variant.images.all().delete()
            from .models import ListingImage
            ListingImage.objects.create(
                listing_variant=variant,
                image_file=new_photo
            )

        variant.attributes.all().delete() 
        attr_names = request.POST.getlist('edit_attr_names[]')
        attr_vals = request.POST.getlist('edit_attr_vals[]')

        for name, val in zip(attr_names, attr_vals):
            if name.strip() and val.strip():
                ProductAttribute.objects.create(variant=variant, name=name, value=val)

        messages.success(request, f"Unit {variant.sku} and attributes updated successfully!")
        return redirect('units')

@login_required(login_url='login')
def delete_variant(request, pk):
    try:
        variant = ListingVariant.objects.get(id=pk)
        sku_deleted = variant.sku
        variant.delete()
        messages.warning(request, f"Successfully deleted unit: {sku_deleted}")
    except ListingVariant.DoesNotExist:
        messages.error(request, "Error: Unit not found.")
    
    return redirect('units')    

@login_required(login_url='login') 
def create_listing(request):

    if request.method == 'POST':
        name = request.POST.get('listing_name')
        category_id = request.POST.get('category_id')
        description = request.POST.get('description')
        
        category = Category.objects.get(id=category_id)
        
        Listing.objects.create(
            category=category,
            name=name,
            description=description,
            listing_status='active'
        )
    
    return redirect('units')

@login_required(login_url='login')
def inventory_listings(request):
    if request.method == 'POST':
        uploaded_images = request.FILES.getlist('thumbnail')
        main_thumbnail = uploaded_images[0] if uploaded_images else None
        
        listing_name = request.POST.get('listing_name')
        category_id = request.POST.get('category_id')
        activity_id = request.POST.get('activity_id')
        description = request.POST.get('description')
        brand = request.POST.get('brand')
        tags = request.POST.get('tags')
        vendor = request.POST.get('vendor')
        model_number = request.POST.get('model_number')
        base_price_input = request.POST.get('base_price')
        base_price = base_price_input if base_price_input else None
        thumbnail = request.FILES.get('thumbnail') 
        status = request.POST.get('listing_status', 'active')
        
        if listing_name and category_id:
            category = Category.objects.get(id=category_id)
            activity = None
            if activity_id:
                activity = Activity.objects.get(id=activity_id)
            listing = Listing.objects.create(
                category=category,
                activity=activity,
                name=listing_name,
                brand=brand,
                thumbnail=main_thumbnail,
                tags=tags,
                vendor=vendor,
                model_number=model_number,
                base_price=base_price,
                description=description,
                listing_status=status,
            )
            
        for img in uploaded_images:
                ListingGalleryImage.objects.create(
                    listing=listing, 
                    image_file=img
                )
        return redirect('listings')

    listings = Listing.objects.select_related('category').order_by('-date_created')
    categories = Category.objects.all()
    activities = Activity.objects.all()
    context = {
        'listings': listings,
        'categories': categories,
        'activities': activities
    }
    return render(request, 'inventory/products.html', context)

@login_required(login_url='login')
def edit_listing(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(id=listing_id)
        listing.name = request.POST.get('listing_name')
        listing.brand = request.POST.get('brand')
        listing.vendor = request.POST.get('vendor')
        listing.base_price = request.POST.get('base_price') or None
        listing.model_number = request.POST.get('model_number')
        listing.tags = request.POST.get('tags')
        listing.description = request.POST.get('description')
        listing.listing_status = request.POST.get('listing_status')
        category_id = request.POST.get('category_id')
        activity_id = request.POST.get('activity_id')
        listing.category = Category.objects.get(id=category_id)
        
        if activity_id:
            listing.activity = Activity.objects.get(id=activity_id)
        else:
            listing.activity = None
        
        listing.activity = Activity.objects.get(id=activity_id)
        
        price = request.POST.get('base_price')
        listing.base_price = price if price else None
        
        if request.FILES.get('thumbnail'):
            listing.thumbnail = request.FILES.get('thumbnail')
            
        listing.save()
        messages.success(request, f"Product {listing.name} updated successfully!")
        return redirect('listings')
    
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    product_name = listing.name
    listing.delete()
    
    messages.warning(request, f"Product '{product_name}' and its variants have been permanently removed.")
    return redirect('listings')


@login_required(login_url='login')
def display_category(request):
    if request.method == 'POST':
        new_category_name = request.POST.get('category_name')
        if new_category_name:
            Category.objects.create(category_name=new_category_name)
        return redirect('category')

    categories = Category.objects.all().order_by('-date_created')
    
    context = {
        'categories': categories
    }
    
    return render(request, 'inventory/category.html', context)

@login_required(login_url='login')
def edit_category(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)
        
        category.category_name = request.POST.get('category_name')
        category.save()
        
        messages.success(request, f"Category '{category.category_name}' updated!")
        return redirect('category')
    
@login_required(login_url='login')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.category_name
    
    if category.listings.exists():
        messages.error(request, f"Cannot delete '{name}' because it contains products!")
    else:
        category.delete()
        messages.warning(request, f"Category '{name}' deleted.")
        
    return redirect('category')

@login_required(login_url='login')
def display_activity(request):
    if request.method == 'POST':
        new_activity_name = request.POST.get('activity_name')
        if new_activity_name:
            Activity.objects.create(activity_name=new_activity_name)
        return redirect('activity')

    activities = Activity.objects.all().order_by('-date_created')
    
    context = {
        'activities': activities
    }
    
    return render(request, 'inventory/activity.html', context)

@login_required(login_url='login')
def edit_activity(request):
    if request.method == 'POST':
        activity_id = request.POST.get('activity_id')
        activity = get_object_or_404(Activity, id=activity_id)
        
        activity.activity_name = request.POST.get('activity_name')
        activity.save()
        
        messages.success(request, f"Activity '{activity.activity_name}' updated!")
        return redirect('activity')
    
@login_required(login_url='login')
def delete_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    name = activity.activity_name
    
    if activity.listings.exists():
        messages.error(request, f"Cannot delete '{name}' because it contains products!")
    else:
        activity.delete()
        messages.warning(request, f"Activity '{name}' deleted.")
        
    return redirect('activity')

@login_required(login_url='login')
def stock_ledger_list(request):
    entries = StockLedger.objects.all().select_related('variant__listing', 'staff')
    return render(request, 'inventory/ledger.html', {'ledger_entries': entries})