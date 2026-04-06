from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from AginodOutdoorShop.decorators import staff_member_required
from .models import ListingVariant, Listing, ListingImage, Category, ProductAttribute, StockLedger, Activity, ListingGalleryImage

@staff_member_required
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
        
        if len(variant_images) > 1:
            for img in variant_images[1:]:
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

    variants = (
        ListingVariant.objects
        .select_related('listing__category')
        .prefetch_related('attributes', 'images')
        .order_by('-date_created', '-id')
    )
    listings = Listing.objects.all()
    return render(request, 'inventory/units.html', {'variants': variants, 'listings': listings})

@staff_member_required
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
        variant.status = status
        
        new_thumbnail = request.FILES.get('variant_image') 
        if new_thumbnail:
            if variant.thumbnail:
                variant.thumbnail.delete(save=False) 
            variant.thumbnail = new_thumbnail
            
        variant.save()
        
        images_to_delete = request.POST.getlist('delete_images[]')
        if images_to_delete:
            from .models import ListingImage
            images = ListingImage.objects.filter(id__in=images_to_delete, listing_variant=variant)
            for img in images:
                img.image_file.delete(save=False)
                img.delete()

        new_gallery_images = request.FILES.getlist('new_variant_images')
        if new_gallery_images:
            from .models import ListingImage
            for img in new_gallery_images:
                ListingImage.objects.create(
                    listing_variant=variant,
                    image_file=img
                )

        variant.attributes.all().delete() 
        attr_names = request.POST.getlist('edit_attr_names[]')
        attr_vals = request.POST.getlist('edit_attr_vals[]')

        for name, val in zip(attr_names, attr_vals):
            if name.strip() and val.strip():
                ProductAttribute.objects.create(variant=variant, name=name, value=val)

        messages.success(request, f"Unit {variant.sku} updated successfully!")
        return redirect('units')

@staff_member_required
def delete_variant(request, pk):
    try:
        variant = ListingVariant.objects.get(id=pk)
        sku_deleted = variant.sku
        variant.delete()
        messages.warning(request, f"Successfully deleted unit: {sku_deleted}")
    except ListingVariant.DoesNotExist:
        messages.error(request, "Error: Unit not found.")
    
    return redirect('units')    

@staff_member_required 
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

@staff_member_required
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
        status = request.POST.get('listing_status', 'active')
        gender = request.POST.get('gender', 'unisex')
        valid_genders = {c[0] for c in Listing.GENDER_CHOICES}
        if gender not in valid_genders:
            gender = 'unisex'
        
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
                gender=gender,
            )
            
            if len(uploaded_images) > 1:
                for img in uploaded_images[1:]:
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

@staff_member_required
def edit_listing(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        listing = get_object_or_404(Listing, id=listing_id)
        
        listing.name = request.POST.get('listing_name')
        listing.brand = request.POST.get('brand')
        listing.vendor = request.POST.get('vendor')
        listing.model_number = request.POST.get('model_number')
        listing.tags = request.POST.get('tags')
        listing.description = request.POST.get('description')
        listing.gender = request.POST.get('gender')
        listing.listing_status = request.POST.get('listing_status')
        
        price = request.POST.get('base_price')
        listing.base_price = price if price else None
        
        category_id = request.POST.get('category_id')
        if category_id:
            listing.category = Category.objects.get(id=category_id)
        
        activity_id = request.POST.get('activity_id')
        if activity_id:
            listing.activity = Activity.objects.get(id=activity_id)
        else:
            listing.activity = None
            
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


@staff_member_required
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

@staff_member_required
def edit_category(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)
        
        category.category_name = request.POST.get('category_name')
        category.save()
        
        messages.success(request, f"Category '{category.category_name}' updated!")
        return redirect('category')
    
@staff_member_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.category_name
    
    if category.listings.exists():
        messages.error(request, f"Cannot delete '{name}' because it contains products!")
    else:
        category.delete()
        messages.warning(request, f"Category '{name}' deleted.")
        
    return redirect('category')

@staff_member_required
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

@staff_member_required
def edit_activity(request):
    if request.method == 'POST':
        activity_id = request.POST.get('activity_id')
        activity = get_object_or_404(Activity, id=activity_id)
        
        activity.activity_name = request.POST.get('activity_name')
        activity.save()
        
        messages.success(request, f"Activity '{activity.activity_name}' updated!")
        return redirect('activity')
    
@staff_member_required
def delete_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    name = activity.activity_name
    
    if activity.listings.exists():
        messages.error(request, f"Cannot delete '{name}' because it contains products!")
    else:
        activity.delete()
        messages.warning(request, f"Activity '{name}' deleted.")
        
    return redirect('activity')

@staff_member_required
def stock_ledger_list(request):
    entries = StockLedger.objects.all().select_related('variant__listing', 'staff')
    return render(request, 'inventory/ledger.html', {'ledger_entries': entries})