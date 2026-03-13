"""
URL configuration for AginodOutdoorShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from OutdoorShop import views as shop_views
from inventory import views as inventory_views
from AginodOutdoorShop import views as global_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('manage/admin', admin.site.urls),
    path('', shop_views.home, name='home'),
    path('manage/login/', global_views.login, name='login'),
    path('manage/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('manage/', global_views.dashboard, name='dashboard'),
    path('manage/inventory/', include('inventory.urls')),
    path('manage/pos/', include(('sales.urls', 'sales'), namespace='sales'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
