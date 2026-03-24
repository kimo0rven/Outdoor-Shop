from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .models import Category, Listing, ListingVariant, StockLedger, Activity, ProductAttribute
from accounts.models import User as Accounts
from sales.models import Order, OrderItem


class ListingVariantInline(admin.TabularInline):
    model = ListingVariant
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'item_total')

class ProductAttributeOnline(admin.TabularInline):
    model = ProductAttribute
    extra = 0

class OrdersInline(admin.TabularInline):
    model = Order
    fk_name = 'user'
    extra = 0
    verbose_name = "Placed Order"
    verbose_name_plural = "Placed Orders"
    readonly_fields = ('total_amount', 'status', 'order_date')

class OrdersProcessedInline(admin.TabularInline):
    model = Order
    fk_name = 'processed_by'
    extra = 0
    verbose_name = "Processed Order"
    verbose_name_plural = "Processed Orders"
    readonly_fields = ('order_date', 'total_amount', 'status')

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('username', "first_name", "last_name", 'is_staff', 'is_customer', 'is_superuser')
    
    def get_inlines(self, request, obj=None):
        inlines = []
        if obj:
            if obj.is_customer:
                inlines.append(OrdersInline)
            if obj.is_staff:
                inlines.append(OrdersProcessedInline)
        return inlines

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('admin_thumbnail', 'name', 'category', 'activity', 'listing_status', 'timestamps')
    list_editable = ('activity', 'category', 'listing_status')
    list_display_links = ('admin_thumbnail', 'name')
    list_filter = ('listing_status', 'category')
    search_fields = ('name', 'description')
    
    def admin_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="width: 45px; height:45px; object-fit:contain;" />', obj.thumbnail.url)
        return "No Image"
    
    def timestamps(self, obj):
        created = obj.date_created.strftime("%b %d, %y | %I:%M %p")
        modified = obj.date_modified.strftime("%b %d, %y | %I:%M %p")
        return format_html(
            '<span style="font-size: 11px; color: #888;">Add: {}</span><br>'
            '<span style="font-size: 11px; color: #aaa;">Mod: {}</span>',
            created, modified
        )

    timestamps.short_description = 'Timestamps'
    admin_thumbnail.short_description = 'Preview'
    
    inlines = [ListingVariantInline]
    
    class Media:
        css = {
            'all': ('inventory/css/admin_custom.css',)
        }
    

@admin.register(ListingVariant)
class VariantsAdmin(admin.ModelAdmin):
    list_display = (
        'admin_thumbnail', 
        'variant_name', 
        'parent_listing_link', 
        'sku', 
        'price', 
        'colored_stock',
        'current_stock_quantity',
        'status',
        'timestamps',
    )
    list_editable = ('price', 'current_stock_quantity', 'status')
    list_display_links = ('admin_thumbnail', 'variant_name', 'sku')
    list_filter = ('status',)
    search_fields = ('variant_name', 'sku', 'listing__name', 'listing__brand')
    
    def colored_stock(self, obj):
        if obj.current_stock_quantity <= 5:
            return format_html(
                '<span style="color: #ff4444; font-weight: bold;">LOW</span>', 
                obj.current_stock_quantity
            )
        return format_html(
                '<span style="color: #fff; font-weight: bold; vertical-align: none;">NORMAL</span>', 
                obj.current_stock_quantity
            )
    
    def parent_listing_link(self, obj):
        if obj.listing:
            url = reverse('admin:inventory_listing_change', args=[obj.listing.id])
            return format_html('<a href="{}" style="font-weight:bold;">{}</a>', url, obj.listing.name)
        return "-"
    
    def admin_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="width: 45px; height:45px; object-fit:contain;" />', obj.thumbnail.url)
        return "No Image"
    
    def timestamps(self, obj):
        created = obj.date_created.strftime("%b %d, %y | %I:%M %p")
        modified = obj.date_modified.strftime("%b %d, %y | %I:%M %p")
        return format_html(
            '<span style="font-size: 11px; color: #888;">Add: {}</span><br>'
            '<span style="font-size: 11px; color: #aaa;">Mod: {}</span>',
            created, modified
        )
    
    colored_stock.short_description = 'Stock'
    colored_stock.admin_order_field = 'current_stock_quantity'
    parent_listing_link.short_description = 'Parent Listing'
    admin_thumbnail.short_description = 'Preview'
    
    inlines = [ProductAttributeOnline]
    
    class Media:
        css = {
            'all': ('inventory/css/admin_custom.css',)
        }
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_amount', 'colored_status', 'order_source', 'order_date')
    list_filter = ('status', 'order_source', 'order_date')
    readonly_fields = ('order_date', 'date_modified')
    
    def customer_name(self, obj):
        return obj.user.get_full_name() if obj.user else "Guest/Deleted"
    
    def colored_status(self, obj):
        colors = {
            'pending': '#ff9800',
            'completed': '#4caf50',
            'cancelled': '#f44336',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'),
            obj.get_status_display()
        )
    
    colored_status.short_description = 'Status'
    inlines = [OrderItemInline]


@admin.register(StockLedger)
class InventoryLedgerAdmin(admin.ModelAdmin):
    list_display = ('variant', 'transaction_type', 'quantity_changed', 'previous_stock', 'new_stock', 'date_created')
    list_filter = ('transaction_type', 'date_created')
    search_fields = ('variant__sku', 'reference_note')
    
    readonly_fields = (
        'variant', 
        'staff', 
        'transaction_type', 
        'quantity_changed', 
        'previous_stock', 
        'new_stock', 
        'reference_note', 
        'date_created'
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Category)
admin.site.register(Activity)
