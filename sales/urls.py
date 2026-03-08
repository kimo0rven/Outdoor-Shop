from django.contrib import admin
from django.urls import path
from sales import views as sales_view

urlpatterns = [
    path('', sales_view.pos_home, name='pos_home'),
    path('search/', sales_view.pos_search_products, name='pos_search'),
    path('checkout/', sales_view.process_checkout, name='pos_checkout'),
    path('orders/', sales_view.order_list, name='order_history'),
]
