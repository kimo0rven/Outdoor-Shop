import os
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

def generate_image_path(instance, filename):
    model_name = instance.__class__.__name__
    
    if model_name == 'ListingImage':
        parent_id = instance.listing_variant.listing.id
        sku = instance.listing_variant.sku
        return f'products/{parent_id}/{sku}/{filename}'

    elif model_name == 'ListingGalleryImage':
        parent_id = instance.listing.id if instance.listing.id else 'temp'
        return f'products/{parent_id}/gallery/{filename}'
    
    elif model_name == 'ListingVariant':
        parent_id = instance.listing.id
        var_id = instance.id if instance.id else 'temp'
        return f'products/{parent_id}/variants/{var_id}/thumbnail_{filename}'
    
    else:
        prod_id = instance.id if instance.id else 'temp'
        return f'products/{prod_id}/thumbnail_{filename}'

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name
    
class Activity(models.Model):
    activity_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
    
    def __str__(self):
        return self.activity_name

class SizeGuide(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, blank=True)
    measurements = models.JSONField(default=dict)
    
    def __str__(self):
        return self.name

class Listing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=150, blank=True, null=True) 
    thumbnail = models.ImageField(upload_to=generate_image_path, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.CharField(max_length=150, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    size_guide = models.ForeignKey(
        SizeGuide, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='listings'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Listing"
        verbose_name_plural = "Product Listings"

    def __str__(self):
        return f"{self.brand} {self.name}" if self.brand else self.name

class ListingVariant(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
        ('damaged', 'Damaged/Hold'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=255, default="Standard") 
    sku = models.CharField(max_length=100, unique=True)
    thumbnail = models.ImageField(upload_to=generate_image_path, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock_quantity = models.PositiveIntegerField(verbose_name="Stock Level", default=0)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='in_stock'
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
    

    def __str__(self):
        return f"{self.listing.name} - {self.sku}"

    @property
    def is_available(self):
        return self.current_stock_quantity > 0 and self.status == 'in_stock'

class ProductAttribute(models.Model):
    variant = models.ForeignKey(ListingVariant, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}: {self.value}"

class ListingImage(models.Model):
    listing_variant = models.ForeignKey(ListingVariant, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to=generate_image_path)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Image for {self.listing_variant.sku}"
    
class ListingGalleryImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='gallery')
    image_file = models.ImageField(upload_to=generate_image_path)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery Image for {self.listing.name}"

@receiver(post_save, sender=Listing)
def move_listing_thumbnail(sender, instance, created, **kwargs):
    if created and instance.thumbnail:
        old_path = instance.thumbnail.path
        new_dir = os.path.join(settings.MEDIA_ROOT, f'products/{instance.id}')
        new_filename = f"thumbnail_{os.path.basename(old_path)}"
        new_path = os.path.join(new_dir, new_filename)

        os.makedirs(new_dir, exist_ok=True)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            relative_new_path = f'products/{instance.id}/{new_filename}'
            Listing.objects.filter(id=instance.id).update(thumbnail=relative_new_path)


@receiver(post_save, sender=ListingVariant)
def move_variant_thumbnail(sender, instance, created, **kwargs):
    if created and instance.thumbnail:
        old_path = instance.thumbnail.path
        new_dir = os.path.join(settings.MEDIA_ROOT, f'products/{instance.listing.id}/variants/{instance.id}')
        new_filename = f"thumbnail_{os.path.basename(old_path)}"
        new_path = os.path.join(new_dir, new_filename)

        os.makedirs(new_dir, exist_ok=True)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            relative_new_path = f'products/{instance.listing.id}/variants/{instance.id}/{new_filename}'
            ListingVariant.objects.filter(id=instance.id).update(thumbnail=relative_new_path)

class StockLedger(models.Model):
    TRANSACTION_TYPES = [
        ('receive', 'Stock In (Restock)'),
        ('sale', 'Stock Out (Sale)'),
        ('adjustment', 'Manual Adjustment'),
        ('return', 'Customer Return'),
    ]

    variant = models.ForeignKey(ListingVariant, on_delete=models.CASCADE, related_name='ledger_entries')
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'is_staff': True}
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity_changed = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_note = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.variant.sku} | {self.transaction_type} | {self.quantity_changed}"