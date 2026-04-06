from django.contrib import admin
from django.urls import path
from sales import views as sales_view

urlpatterns = [
    path('', sales_view.pos_home, name='pos_home'),
    path('search/', sales_view.pos_search_products, name='pos_search'),
    path('pos/variants/<int:listing_id>/', sales_view.pos_get_variants, name='pos_get_variants'),
    path('checkout/', sales_view.process_checkout, name='pos_checkout'),
    path('orders/', sales_view.sales_order, name='order_history'),
    path('orders/<int:order_id>/', sales_view.sales_order_detail, name='sales_order_detail'),
    path('orders/<int:order_id>/status/', sales_view.sales_order_update_status, name='sales_order_update_status'),
]
