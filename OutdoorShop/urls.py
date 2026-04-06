from django.urls import path, include
from OutdoorShop import views as shop_views
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('products/<int:pk>/', shop_views.product_detail, name='product_detail'),
    path('products/all/', shop_views.all_products, name='all_products'),
    path('products/search/', shop_views.search_products, name='search_products'),
    path('cart/', shop_views.cart_detail, name='cart_detail'),
    path('cart/add/', shop_views.cart_add, name='cart_add'),
    path('cart/remove/', shop_views.cart_remove, name='cart_remove'),
    path('cart/update/', shop_views.cart_update, name='cart_update'),
    path('checkout/', shop_views.checkout, name='checkout'),
    path('checkout/save-address/', shop_views.save_address, name='save_address'),
    path('process-order/', shop_views.process_order, name='process_order'),
    path('order-success/', shop_views.order_success, name='order_success'),
    path('order/<int:order_id>/update-status/', shop_views.update_order_status, name='update_order_status'),
    path('account/', RedirectView.as_view(pattern_name='profile', permanent=False), name='profile'),
    path('account/profile/', shop_views.profile, name='profile'),
    path('account/address-book/', shop_views.address_book, name='address_book'),
    path('account/address/new/', shop_views.address_create, name='address_create'),
    path('account/address/<int:address_id>/edit/', shop_views.address_edit, name='address_edit'),
    path('account/address/<int:address_id>/set-default/', shop_views.set_default_address, name='set_default_address'),
    path('account/address/<int:address_id>/delete/', shop_views.address_delete, name='address_delete'),
    path('account/register/', accounts_views.register_view, name='register'),
    path('account/login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('account/orders/', shop_views.order_history, name='order_history'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
