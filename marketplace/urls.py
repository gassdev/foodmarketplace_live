from django.urls import path
from . import views

urlpatterns = [
    path('', views.markeplate, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_details, name='vendor-details'),

    # ADD TO CART
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add-to-cart'),
    # DECREASE CART
    path('decrease-cart/<int:food_id>/', views.decrease_cart, name='decrease-cart'),
    # DELETE CART ITEM
    path('delete-cart/<int:cart_id>/', views.delete_cart, name='delete-cart'),
]
