from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from accounts.models import ShippingAddress, User
from sales.models import Order, OrderItem, Payment

from .models import (
    Activity,
    Category,
    Listing,
    ListingGalleryImage,
    ListingImage,
    ListingVariant,
    ProductAttribute,
    SizeGuide,
    StockLedger,
)


# --- Inlines -----------------------------------------------------------------


class ListingVariantInline(admin.TabularInline):
    model = ListingVariant
    extra = 0
    fields = ('variant_name', 'sku', 'price', 'current_stock_quantity', 'status', 'thumbnail')
    show_change_link = True


class ListingGalleryImageInline(admin.TabularInline):
    model = ListingGalleryImage
    extra = 0
    fields = ('image_file',)


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 0
    fields = ('name', 'value')


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 0
    fields = ('image_file',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ('listing_variant',)
    readonly_fields = ('price', 'item_total')


class OrdersInline(admin.TabularInline):
    model = Order
    fk_name = 'user'
    extra = 0
    show_change_link = True
    verbose_name = 'Placed order'
    verbose_name_plural = 'Placed orders'
    fields = ('id', 'total_amount', 'status', 'order_source', 'order_date')
    readonly_fields = fields


class OrdersProcessedInline(admin.TabularInline):
    model = Order
    fk_name = 'processed_by'
    extra = 0
    show_change_link = True
    verbose_name = 'Processed order'
    verbose_name_plural = 'Processed orders'
    fields = ('id', 'user', 'total_amount', 'status', 'order_date')
    readonly_fields = fields


class ShippingAddressInline(admin.TabularInline):
    model = ShippingAddress
    extra = 0
    fields = (
        'first_name',
        'last_name',
        'phone_number',
        'address_line_1',
        'address_line_2',
        'city',
        'state',
        'postal_code',
        'country',
        'is_default',
    )
    readonly_fields = fields


# --- Inventory catalog -------------------------------------------------------


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'listing_count', 'date_created', 'date_modified')
    list_display_links = ('category_name',)
    search_fields = ('category_name',)
    ordering = ('category_name',)
    readonly_fields = ('date_created', 'date_modified')

    @admin.display(description='Listings', ordering='listing_count')
    def listing_count(self, obj):
        return getattr(obj, 'listing_count', 0)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(listing_count=Count('listings'))


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_name', 'listing_count', 'date_created', 'date_modified')
    list_display_links = ('activity_name',)
    search_fields = ('activity_name',)
    ordering = ('activity_name',)
    readonly_fields = ('date_created', 'date_modified')

    @admin.display(description='Listings', ordering='listing_count')
    def listing_count(self, obj):
        return getattr(obj, 'listing_count', 0)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(listing_count=Count('listings'))


@admin.register(SizeGuide)
class SizeGuideAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'listing_count')
    search_fields = ('name', 'brand')
    ordering = ('name',)

    @admin.display(description='Listings', ordering='listing_count')
    def listing_count(self, obj):
        return getattr(obj, 'listing_count', 0)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(listing_count=Count('listings'))


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'admin_thumbnail',
        'name',
        'brand',
        'category',
        'activity',
        'gender',
        'variant_count',
        'base_price',
        'listing_status',
        'timestamps',
    )
    list_display_links = ('admin_thumbnail', 'name')
    list_editable = ('category', 'activity', 'gender', 'listing_status')
    list_filter = (
        'listing_status',
        'gender',
        'category',
        'activity',
    )
    search_fields = (
        'name',
        'brand',
        'description',
        'tags',
        'vendor',
        'model_number',
    )
    autocomplete_fields = ('category', 'activity', 'size_guide')
    readonly_fields = ('date_created', 'date_modified')
    inlines = (ListingVariantInline, ListingGalleryImageInline)
    list_per_page = 50
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'brand',
                'category',
                'activity',
                'gender',
                'listing_status',
            ),
        }),
        ('Pricing & supplier', {
            'fields': ('base_price', 'vendor', 'model_number', 'tags'),
        }),
        ('Media & content', {
            'fields': ('thumbnail', 'description', 'size_guide'),
        }),
        ('Timestamps', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )

    class Media:
        css = {'all': ('inventory/css/admin_custom.css',)}

    @admin.display(description='Preview')
    def admin_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" alt="" style="width:45px;height:45px;object-fit:contain;" />',
                obj.thumbnail.url,
            )
        return '—'

    @admin.display(description='Variants', ordering='variant_count')
    def variant_count(self, obj):
        return getattr(obj, 'variant_count', 0)

    @admin.display(description='Timestamps')
    def timestamps(self, obj):
        created = obj.date_created.strftime('%b %d, %y · %I:%M %p')
        modified = obj.date_modified.strftime('%b %d, %y · %I:%M %p')
        return format_html(
            '<span style="font-size:11px;color:#666;">Created {}</span><br>'
            '<span style="font-size:11px;color:#999;">Modified {}</span>',
            created,
            modified,
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('category', 'activity')
            .annotate(variant_count=Count('variants', distinct=True))
        )


@admin.register(ListingVariant)
class ListingVariantAdmin(admin.ModelAdmin):
    list_display = (
        'admin_thumbnail',
        'variant_name',
        'parent_listing_link',
        'sku',
        'price',
        'stock_level_display',
        'current_stock_quantity',
        'status',
        'timestamps',
    )
    list_display_links = ('admin_thumbnail', 'variant_name', 'sku')
    list_editable = ('price', 'current_stock_quantity', 'status')
    list_filter = (
        'status',
        'listing__listing_status',
        'listing__category',
        'listing__gender',
    )
    search_fields = (
        'sku',
        'variant_name',
        'listing__name',
        'listing__brand',
    )
    autocomplete_fields = ('listing',)
    readonly_fields = ('date_created', 'date_modified')
    inlines = (ProductAttributeInline, ListingImageInline)
    list_select_related = ('listing', 'listing__category')
    list_per_page = 50
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': ('listing', 'variant_name', 'sku', 'status'),
        }),
        ('Pricing & inventory', {
            'fields': ('price', 'current_stock_quantity', 'thumbnail'),
        }),
        ('Timestamps', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )

    class Media:
        css = {'all': ('inventory/css/admin_custom.css',)}

    @admin.display(description='Preview')
    def admin_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" alt="" style="width:45px;height:45px;object-fit:contain;" />',
                obj.thumbnail.url,
            )
        return '—'

    @admin.display(description='Parent listing', ordering='listing__name')
    def parent_listing_link(self, obj):
        if not obj.listing_id:
            return '—'
        url = reverse('admin:inventory_listing_change', args=[obj.listing_id])
        label = obj.listing.name
        if obj.listing.brand:
            label = f'{obj.listing.brand} · {label}'
        return format_html('<a href="{}"><strong>{}</strong></a>', url, label)

    @admin.display(description='Stock flag', ordering='current_stock_quantity')
    def stock_level_display(self, obj):
        qty = obj.current_stock_quantity
        if obj.status != 'in_stock':
            return format_html(
                '<span style="color:#888;font-weight:600;">{}</span>',
                obj.get_status_display(),
            )
        if qty <= 0:
            return mark_safe('<span style="color:#c62828;font-weight:700;">OUT</span>')
        if qty <= 5:
            return format_html(
                '<span style="color:#e65100;font-weight:700;">LOW ({})</span>',
                qty,
            )
        return format_html(
            '<span style="color:#2e7d32;font-weight:600;">OK ({})</span>',
            qty,
        )

    @admin.display(description='Timestamps')
    def timestamps(self, obj):
        created = obj.date_created.strftime('%b %d, %y · %I:%M %p')
        modified = obj.date_modified.strftime('%b %d, %y · %I:%M %p')
        return format_html(
            '<span style="font-size:11px;color:#666;">{}</span><br>'
            '<span style="font-size:11px;color:#999;">{}</span>',
            created,
            modified,
        )


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = (
        'date_created',
        'variant_link',
        'transaction_type',
        'quantity_changed',
        'previous_stock',
        'new_stock',
        'staff',
        'reference_note_short',
    )
    list_filter = ('transaction_type', 'date_created')
    search_fields = (
        'variant__sku',
        'variant__listing__name',
        'reference_note',
        'staff__username',
    )
    date_hierarchy = 'date_created'
    list_select_related = ('variant', 'variant__listing', 'staff')
    ordering = ('-date_created',)
    readonly_fields = (
        'variant',
        'staff',
        'transaction_type',
        'quantity_changed',
        'previous_stock',
        'new_stock',
        'reference_note',
        'date_created',
    )

    @admin.display(description='Variant', ordering='variant__sku')
    def variant_link(self, obj):
        url = reverse('admin:inventory_listingvariant_change', args=[obj.variant_id])
        return format_html(
            '<a href="{}"><strong>{}</strong></a><br>'
            '<span style="font-size:11px;color:#666;">{}</span>',
            url,
            obj.variant.sku,
            obj.variant.listing.name,
        )

    @admin.display(description='Note')
    def reference_note_short(self, obj):
        if not obj.reference_note:
            return '—'
        text = obj.reference_note
        return text[:48] + '…' if len(text) > 48 else text

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Allow opening the read-only change view for audit detail.
        return True


# --- Accounts & sales (registered here for a single staff admin hub) --------


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_customer',
        'is_superuser',
        'is_active',
    )
    list_filter = ('is_staff', 'is_customer', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'gender')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_customer',
                'groups',
                'user_permissions',
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_inlines(self, request, obj=None):
        inlines = []
        if obj:
            if obj.is_customer:
                inlines.append(OrdersInline)
                inlines.append(ShippingAddressInline)
            if obj.is_staff:
                inlines.append(OrdersProcessedInline)
        return inlines


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_display',
        'total_amount',
        'colored_status',
        'order_source',
        'order_date',
        'payment_summary',
    )
    list_filter = ('status', 'order_source', 'order_date')
    search_fields = (
        'id',
        'user__username',
        'user__email',
        'payment__transaction_id',
    )
    autocomplete_fields = ('user', 'processed_by', 'shipping_address')
    readonly_fields = ('order_date', 'date_modified')
    inlines = (OrderItemInline,)
    list_select_related = ('user', 'payment')
    date_hierarchy = 'order_date'
    ordering = ('-order_date',)
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'processed_by',
                'shipping_address',
                'total_amount',
                'status',
                'order_source',
            ),
        }),
        ('Timestamps', {
            'fields': ('order_date', 'date_modified'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Customer', ordering='user__username')
    def customer_display(self, obj):
        if not obj.user_id:
            return mark_safe('<span style="color:#999;">Guest / removed</span>')
        url = reverse('admin:accounts_user_change', args=[obj.user_id])
        name = obj.user.get_full_name() or obj.user.username
        return format_html('<a href="{}">{}</a>', url, name)

    @admin.display(description='Status', ordering='status')
    def colored_status(self, obj):
        colors = {
            'pending': '#f57c00',
            'processing': '#1976d2',
            'shipped': '#7b1fa2',
            'delivered': '#388e3c',
            'completed': '#2e7d32',
            'cancelled': '#c62828',
            'returned': '#6a1b9a',
            'refunded': '#546e7a',
        }
        color = colors.get(obj.status, '#333')
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description='Payment')
    def payment_summary(self, obj):
        try:
            p = obj.payment
        except Payment.DoesNotExist:
            return '—'
        parts = [p.get_method_display(), p.payment_status or '']
        if p.transaction_id:
            parts.append(p.transaction_id[:20] + ('…' if len(p.transaction_id) > 20 else ''))
        return format_html(
            '<span style="font-size:12px;">{}</span>',
            ' · '.join(x for x in parts if x),
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order_link',
        'amount',
        'method',
        'payment_status',
        'payment_date',
        'transaction_id',
    )
    list_filter = ('method', 'payment_status', 'payment_date')
    search_fields = ('transaction_id', 'order__id', 'order__user__username')
    autocomplete_fields = ('order',)
    readonly_fields = ('payment_date', 'date_modified')
    ordering = ('-payment_date',)

    @admin.display(description='Order', ordering='order_id')
    def order_link(self, obj):
        url = reverse('admin:sales_order_change', args=[obj.order_id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order_id)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        'short_label',
        'user_link',
        'city',
        'state',
        'postal_code',
        'is_default',
        'date_created',
    )
    list_filter = ('is_default', 'country', 'date_created')
    search_fields = (
        'first_name',
        'last_name',
        'city',
        'phone_number',
        'user__username',
        'user__email',
    )
    autocomplete_fields = ('user',)
    readonly_fields = ('date_created', 'date_modified')
    ordering = ('-is_default', '-date_created')

    @admin.display(description='Address', ordering='last_name')
    def short_label(self, obj):
        line = obj.address_line_1[:40] + '…' if len(obj.address_line_1) > 40 else obj.address_line_1
        return f'{obj.first_name} {obj.last_name} — {line}'

    @admin.display(description='User', ordering='user__username')
    def user_link(self, obj):
        if not obj.user_id:
            return '—'
        url = reverse('admin:accounts_user_change', args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
