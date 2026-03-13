import os
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name
    
def listing_thumbnail_path(instance, filename):
    if instance.id:
        return f'products/{instance.id}/thumbnail_{filename}'
    return f'products/temp/thumbnail_{filename}'    

class Listing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=150, blank=True, null=True) 
    thumbnail = models.ImageField(upload_to=listing_thumbnail_path, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.CharField(max_length=150, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.name}" if self.brand else self.name

@receiver(post_save, sender=Listing)
def move_listing_thumbnail(sender, instance, created, **kwargs):
    if created and instance.thumbnail:
        old_path = instance.thumbnail.path
        new_dir = os.path.join(settings.MEDIA_ROOT, f'products/{instance.id}')
        new_filename = f"thumbnail_{os.path.basename(old_path)}"
        new_path = os.path.join(new_dir, new_filename)

        os.makedirs(new_dir, exist_ok=True)

        os.rename(old_path, new_path)
        relative_new_path = f'products/{instance.id}/{new_filename}'
        Listing.objects.filter(id=instance.id).update(thumbnail=relative_new_path)
    
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock_quantity = models.PositiveIntegerField(default=0) 
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='in_stock'
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.listing.name} - {self.sku}"

    @property
    def is_available(self):
        return self.current_stock_quantity > 0 and self.status == 'in_stock'

class ProductAttribute(models.Model):
    variant = models.ForeignKey('ListingVariant', on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __cl__ (self):
        return f"{self.name}: {self.value}"

def variant_image_path(instance, filename):
    product_id = instance.listing_variant.listing.id
    return f'products/{product_id}/{instance.listing_variant.sku}/{filename}'

class ListingImage(models.Model):
    listing_variant = models.ForeignKey(ListingVariant, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to=variant_image_path)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Image for {self.listing_variant.sku}"
    
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