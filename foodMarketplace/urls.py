from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as marketplace_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),

     # CART
    path('cart/', marketplace_views.cart, name='cart'),
    # SEARCH
    path('search/', marketplace_views.search, name='search'),

    # CHECKOUT
    path('checkout/', marketplace_views.checkout, name='checkout'),

    # ORDERS
    path('orders/', include('orders.urls'))
]

if settings.DEBUG:
    urlpatterns += static(
            settings.MEDIA_URL,
            document_root = settings.MEDIA_ROOT
        )