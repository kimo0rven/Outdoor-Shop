from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser

class StaffUser(AbstractUser):
    role = models.CharField(max_length=20, default="Staff")
    
    class Meta:
        db_table = 'inventory_staffuser'

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True) #
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

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
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.CharField(max_length=150, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    listing_status = models.CharField(max_length=50, default='active')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.name}" if self.brand else self.name
    
def variant_image_path(instance, filename):
    return f'products/{instance.listing_variant.sku}/{filename}'

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
    staff = models.ForeignKey(StaffUser, on_delete=models.SET_NULL, null=True)
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