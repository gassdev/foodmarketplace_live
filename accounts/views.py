from django.shortcuts import render, redirect
from django.http import HttpRequest
from orders.models import Order

from vendor.forms import VendorForm
from vendor.models import Vendor
from .forms import UserForm
from .models import User, UserProfile
from .utils import detect_user, send_verification_email
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.exceptions import PermissionDenied

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.defaultfilters import slugify
import datetime

# restrict vendor from accessing the customer page
def check_role_vendor(user: User):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# restrict customer from accessing the vendor page
def check_role_customer(user: User):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def register_user(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('user-account')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # create user using the form
            # password = form.cleaned_data['password']
            # user: User = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # create user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user: User = User.objects.create_user(first_name=first_name,
                                        last_name=last_name,
                                        username=username,
                                        email=email,
                                        password=password)
            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered successfully!')

            return redirect('register-user')
    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/users/register.html', context)

def register_vendor(request: HttpRequest):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('user-account')
    elif request.method == 'POST':
        u_form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if u_form.is_valid() and v_form.is_valid():
            first_name = u_form.cleaned_data['first_name']
            last_name = u_form.cleaned_data['last_name']
            username = u_form.cleaned_data['username']
            email = u_form.cleaned_data['email']
            password = u_form.cleaned_data['password']
            user: User = User.objects.create_user(first_name=first_name,
                                        last_name=last_name,
                                        username=username,
                                        email=email,
                                        password=password)
            user.role = User.VENDOR
            user.save()
            vendor: Vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile: UserProfile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, f"Your account has been registered successfully! Please wait for the approval.")
            return redirect('register-vendor')

    else:
        u_form = UserForm()
        v_form = VendorForm()

    context = {
        'u_form': u_form,
        'v_form': v_form
    }
    return render(request, 'accounts/vendor/register.html', context)

def activate(request: HttpRequest, uidb64, token):
    # Activate the user by setting the is_active state to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user: User = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('user-account')
    else:
        messages.error(request, 'Invalid or expired activation link')
        return redirect('user-account')



def login(request: HttpRequest):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('user-account')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('user-account')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request: HttpRequest):
    auth.logout(request)
    messages.info(request,'You are logged out.')
    return redirect('login')

@login_required
def user_account(request: HttpRequest):
    user = request.user
    redirectUrl = detect_user(user)
    return redirect(redirectUrl)


@login_required
@user_passes_test(check_role_customer)
def customer_dashboard(request: HttpRequest):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/users/dashboard.html', context)

@login_required
@user_passes_test(check_role_vendor)
def vendor_dashboard(request: HttpRequest):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by("-created_at")
    recent_orders = orders[:10]

    # current month's revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }
    return render(request, 'accounts/vendor/dashboard.html', context)


def forgot_password(request: HttpRequest):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send reset password link email
            mail_subject = 'Reset Your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgot-password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request: HttpRequest, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user: User = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password.')
        return redirect('reset-password')
    else:
        messages.error(request, 'Invalid or expired link')
        return redirect('user-account')



def reset_password(request: HttpRequest):
    if request.method == 'POST':
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password == password_confirm:
            pk = request.session.get('uid')
            user: User = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match.')
            return redirect('reset-password')
    return render(request, 'accounts/reset_password.html')