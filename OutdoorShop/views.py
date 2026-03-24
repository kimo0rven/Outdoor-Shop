from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db import models
from inventory.models import Listing

def home_main(request):
    new_threshold = timezone.now() - timedelta(days=30)
    
    new_arrivals = Listing.objects.filter(
        date_created__gte=new_threshold
    ).order_by('-date_created')[:12]
    
    if not new_arrivals:
        new_arrivals = Listing.objects.all().order_by('-date_created')[:8]

    return render(request, 'OutdoorShop/home.html', {'new_arrivals': new_arrivals})