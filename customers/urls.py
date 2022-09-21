from django.urls import path
from accounts import views as accountViews
from . import views

urlpatterns = [
    path('', accountViews.customer_dashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my-orders/', views.my_orders, name='my-orders'),
    path('order-details/<int:order_number>/', views.order_details, name='order-details'),
]
