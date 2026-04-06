from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, F, Count
from inventory.models import ListingVariant, StockLedger, Category
from sales.models import Order, OrderItem
from django.utils import timezone
from datetime import timedelta

from AginodOutdoorShop.decorators import staff_member_required


def login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            if user.is_staff:
                auth_login(request, user) 
                return redirect('dashboard')
            else:
                form.add_error(None, "Access denied. This portal is for authorized staff only.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})


@staff_member_required
def dashboard(request):
    total_value = ListingVariant.objects.annotate(
        value=F('price') * F('current_stock_quantity')
    ).aggregate(total=Sum('value'))['total'] or 0

    total_stock = ListingVariant.objects.aggregate(Sum('current_stock_quantity'))['current_stock_quantity__sum'] or 0
    low_stock_items = ListingVariant.objects.select_related('listing').filter(current_stock_quantity__lte=5, current_stock_quantity__gt=0)
    out_of_stock_count = ListingVariant.objects.filter(current_stock_quantity=0).count()
    
    now = timezone.now()
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    revenue_today = Order.objects.filter(order_date__gte=start_today).aggregate(total=Sum('total_amount'))['total'] or 0
    revenue_7d = Order.objects.filter(order_date__gte=last_7_days).aggregate(total=Sum('total_amount'))['total'] or 0
    recent_revenue = Order.objects.filter(order_date__gte=last_30_days).aggregate(total=Sum('total_amount'))['total'] or 0

    orders_today_count = Order.objects.filter(order_date__gte=start_today).count()
    orders_30d_count = Order.objects.filter(order_date__gte=last_30_days).count()
    aov_30d = (recent_revenue / orders_30d_count) if orders_30d_count else 0

    status_counts_qs = Order.objects.values('status').annotate(count=Count('id'))
    status_counts = {row['status']: row['count'] for row in status_counts_qs}
    pending_orders = status_counts.get('pending', 0)
    processing_orders = status_counts.get('processing', 0)
    shipped_orders = status_counts.get('shipped', 0)
    delivered_orders = status_counts.get('delivered', 0)
    
    recent_activity = StockLedger.objects.all().select_related('variant', 'staff')[:5]
    
    category_data = Category.objects.annotate(
        total_qty=Sum('listings__variants__current_stock_quantity')
    ).order_by('-total_qty')

    recent_orders = (
        Order.objects.select_related('user', 'processed_by')
        .order_by('-order_date')[:8]
    )

    top_sellers_30d = (
        OrderItem.objects.filter(order__order_date__gte=last_30_days)
        .select_related('listing_variant__listing')
        .values(
            'listing_variant_id',
            'listing_variant__sku',
            'listing_variant__variant_name',
            'listing_variant__listing__name',
            'listing_variant__listing__brand',
        )
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:8]
    )

    context = {
        'total_value': total_value,
        'total_stock': total_stock,
        'low_stock_items': low_stock_items,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_items.count(),
        'revenue_today': revenue_today,
        'revenue_7d': revenue_7d,
        'recent_revenue': recent_revenue,
        'orders_today_count': orders_today_count,
        'orders_30d_count': orders_30d_count,
        'aov_30d': aov_30d,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'recent_activity': recent_activity,
        'category_data': category_data,
        'recent_orders': recent_orders,
        'top_sellers_30d': top_sellers_30d,
    }
    return render(request, 'dashboard.html', context)