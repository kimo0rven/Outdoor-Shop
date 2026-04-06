from django.db import models
from django.conf import settings
from inventory.models import ListingVariant
from accounts.models import ShippingAddress

class Order(models.Model):
    SOURCE_POS = 'POS'
    SOURCE_WEB = 'Web'
    
    SOURCE_CHOICES = [
        (SOURCE_POS, 'Point of Sale'),
        (SOURCE_WEB, 'Online Website'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,limit_choices_to={'is_customer': True},  related_name='customer_orders')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True},related_name='processed_orders')
    
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='completed')
    shipping_address = models.ForeignKey(
        ShippingAddress, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='shipping_orders'
    )
    
    order_source = models.CharField(
        max_length=20, 
        choices=SOURCE_CHOICES, 
        default=SOURCE_WEB
    )
    
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} ({self.order_source})"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    listing_variant = models.ForeignKey(ListingVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item_total = models.DecimalField(max_digits=12, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.item_total = self.quantity * self.price
        super().save(*args, **kwargs)
        
class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Debit/Credit Card'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default='Completed')
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} ({self.method})"