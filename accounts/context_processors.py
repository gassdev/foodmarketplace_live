from django.http import HttpRequest
from django.conf import settings
from accounts.models import UserProfile
from vendor.models import Vendor

def get_vendor(request: HttpRequest):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)

def get_user_profile(request: HttpRequest):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)

def get_google_api(request: HttpRequest):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}

def get_paypal_client_id(request: HttpRequest):
    return {'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID}

def get_stripe_api_key(request: HttpRequest):
    return {'STRIPE_API_KEY': settings.STRIPE_API_KEY}