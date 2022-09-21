from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name="place-order"),
    path('payments/', views.payments, name="payments"),
    path('order-complete/', views.order_complete, name="order-complete"),
    path('create-checkout-session/', views.create_stripe_checkout_session, name="create-checkout-session"),
    path('stripe-success-payment/<str:session_id>/', views.stripe_success_payment, name="stripe-success-payment"),
]
