from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages

from accounts.views import check_role_customer
from orders.models import Order, OrderedFood
import simplejson as json


@login_required
@user_passes_test(check_role_customer)
def cprofile(request: HttpRequest):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('cprofile')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form':profile_form,
        'user_form':user_form,
        'profile':profile,
    }
    return render(request, 'customers/cprofile.html', context)

@login_required
@user_passes_test(check_role_customer)
def my_orders(request: HttpRequest):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True
        ).order_by(
            '-created_at'
        )

    context = {
        'orders': orders
    }
    return render(request, 'customers/my_orders.html', context)

def order_details(request: HttpRequest, order_number=None):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'customers/order_details.html', context)
    except:
        return redirect('customer')