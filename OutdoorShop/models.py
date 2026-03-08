from django.db import models
from django.conf import settings

# Create your models here.
class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipping_addresses')
    street_address = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    address_type = models.CharField(max_length=50, help_text="e.g., Home, Office")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street_address}, {self.city}"