from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('listings/', views.inventory_listings, name='listings'),
    path('listings/edit/', views.edit_listing, name='edit_listing'),
    path('listings/delete/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('units/', views.inventory_units, name='units'),
    path('units/create/', views.create_listing, name='create_listing'),
    path('units/edit/', views.edit_variant, name='edit_variant'),
    path('units/delete/<int:pk>/', views.delete_variant, name='delete_variant'),
    path('category/', views.display_category, name='category'),
    path('category/edit/', views.edit_category, name='edit_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('ledger/', views.stock_ledger_list, name='ledger'),
]