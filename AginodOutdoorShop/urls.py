from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from OutdoorShop import views as shop_views
from inventory import views as inventory_views
from AginodOutdoorShop import views as global_views
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('manage/admin', admin.site.urls),
    path('', shop_views.home_main, name='home'),
    path('manage/login/', global_views.login, name='staff_login'),
    path(
        'manage/logout/',
        auth_views.LogoutView.as_view(next_page=reverse_lazy('staff_login')),
        name='staff_logout',
    ),
    path('manage/', global_views.dashboard, name='dashboard'),
    path('manage/inventory/', include('inventory.urls')),
    path('manage/pos/', include(('sales.urls', 'sales'), namespace='sales')),
    path('', include('OutdoorShop.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
