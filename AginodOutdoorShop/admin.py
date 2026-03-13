from django.contrib import admin
from inventory.models import Category, Listing, ListingVariant, ListingImage, StockLedger
from sales.models import Category, Listing, ListingVariant, Order, OrderItem


class ListingVariantInline(admin.TabularInline):
    model = ListingVariant
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'item_total')

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'listing_status', 'date_created')
    list_filter = ('listing_status', 'category')
    search_fields = ('name', 'description')
    
    inlines = [ListingVariantInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'order_date')
    list_filter = ('status', 'order_source')
    search_fields = ('id', 'user__email', 'user__first_name') 
    
    inlines = [OrderItemInline]


@admin.register(StockLedger)
class InventoryLedgerAdmin(admin.ModelAdmin):
    list_display = ('listing_variant', 'quantity_change', 'reason', 'order', 'date_created')
    list_filter = ('reason', 'date_created')
    search_fields = ('listing_variant__SKU', 'reason')
    readonly_fields = ('listing_variant', 'quantity_change', 'reason', 'order', 'date_created')



admin.site.register(Category)