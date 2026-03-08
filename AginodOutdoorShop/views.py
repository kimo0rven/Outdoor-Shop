from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from inventory.models import ListingVariant


@login_required(login_url='login')
def dashboard(request):
    total_value = ListingVariant.objects.annotate(
        value=F('price') * F('current_stock_quantity')
    ).aggregate(total=Sum('value'))['total'] or 0

    total_stock = ListingVariant.objects.aggregate(Sum('current_stock_quantity'))['current_stock_quantity__sum'] or 0
    low_stock_items = ListingVariant.objects.filter(current_stock_quantity__lte=5, current_stock_quantity__gt=0)
    out_of_stock_count = ListingVariant.objects.filter(current_stock_quantity=0).count()
    
    # last_30_days = timezone.now() - timedelta(days=30)
    # recent_revenue = Order.objects.filter(date_created__gte=last_30_days).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # recent_activity = StockLedger.objects.all().select_related('variant', 'staff')[:5]
    
    # category_data = Category.objects.annotate(
    #     total_qty=Sum('listings__variants__current_stock_quantity')
    # ).order_by('-total_qty')[:3]

    context = {
        'total_value': total_value,
        'total_stock': total_stock,
        'low_stock_items': low_stock_items,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_items.count(),
        # 'recent_revenue': recent_revenue,
        # 'recent_activity': recent_activity,
        # 'category_data': category_data,
    }
    return render(request, 'dashboard.html', context)