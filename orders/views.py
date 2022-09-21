from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from foodMarketplace.settings import STRIPE_API_KEY

from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from menu.models import FoodItem
from .utils import add_payment_to_order, generate_order_number, move_cart_items_to_ordered_food, save_payment_infos, send_order_confirmation_email_to_customer, send_order_received_email_to_vendor
from .models import Order, OrderedFood, Payment
from .forms import OrderForm
import simplejson as json
from accounts.utils import send_notification
import stripe
stripe.api_key = STRIPE_API_KEY



@login_required
def place_order(request: HttpRequest):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)
    
    # {"vendor_id":{"subtotal":{"tax_type":{"tax_percentage": "tax_amount"}}}}
    get_tax = Tax.objects.filter(is_active=True)
    subtotal=0
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id]=subtotal

        # Calculate the tax data
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 0)
            tax_dict.update({
                tax_type: {
                    str(tax_percentage): str(tax_amount)
                }
            })
            # print(tax_dict)
        
        # Construct total data
        total_data.update({
            fooditem.vendor.id: {str(subtotal): str(tax_dict)}
        })
    # print(total_data)


            

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # order pk is generated
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')

@login_required
def payments(request: HttpRequest):
    # check if if the request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payment details in the payment model
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = save_payment_infos(request.user, transaction_id, payment_method, order.total, status)

        # update the order model
        order = add_payment_to_order(order, payment)


        # move the cart items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        move_cart_items_to_ordered_food(cart_items, order, payment, request.user)

        # send order confirmation email to the customer
        send_order_confirmation_email_to_customer(request, order)


        # send order received email to the vendor
        send_order_received_email_to_vendor(cart_items, order)

        # clear the cart if the payment is success
        cart_items.delete()


        # return back to ajax with the status success or failure
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse('Payments view')

def order_complete(request: HttpRequest):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(
                order_number=order_number,
                payment__transaction_id=transaction_id,
                is_ordered=True
            )
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        
        tax_data = json.loads(order.tax_data)
        # print(tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }

        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')



@login_required
def create_stripe_checkout_session(request: HttpRequest):
    # STRIPE CHECKOUT
    MY_DOMAIN = get_current_site(request)
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        order:Order = Order.objects.get(user=request.user, order_number=order_number)
        tax_data = json.loads(order.tax_data)
        # print('tax dat --> ',tax_data)
        cart_items = Cart.objects.filter(user=request.user)
        lineItems = []
        for item in cart_items:
            # print(item.fooditem.image.url)
            lineItems.append({
                    'price_data': {
                        'currency': 'xof',
                        'product_data': {
                        'name': item.fooditem.food_title,
                        'images': [
                            "http://"+str(MY_DOMAIN)+item.fooditem.image.url
                        ],
                        },
                        'unit_amount': int(item.fooditem.price),
                    },
                    'quantity': item.quantity,
                    })
        for key, value in tax_data.items():
            for i, j in value.items():
                lineItems.append({
                    'price_data':{
                        'currency':'xof',
                        'product_data':{
                            'name': f"{key} ({i})%"
                        },
                        'unit_amount': int(j)
                    },
                    'quantity': 1
                })
            
        # print(lineItems)
        # print('mydomain --> ', MY_DOMAIN)
        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email = request.user.email,
                line_items=lineItems,
                mode='payment',
                success_url= "http://"+str(MY_DOMAIN)+'/orders/stripe-success-payment/{CHECKOUT_SESSION_ID}?order_number='+order_number,
                cancel_url="http://"+str(MY_DOMAIN)+'/cart/',
            )
            # print(f"---> {checkout_session}")
            return redirect(checkout_session.url)
        except Exception as e:
            print(e)
            messages.error(request, 'Stripe session problem. Try again')
        return redirect('cart')
    else:
        return redirect(request, 'Something went wrong. Try again.')


@login_required
def stripe_success_payment(request: HttpRequest, session_id=None):
    order_number = request.GET.get('order_number')
    stripe_session = stripe.checkout.Session.retrieve(session_id)
    if order_number is not None:
        # print('order number --> ', order_number)
        try:
            order: Order = Order.objects.get(order_number=order_number)
            transaction_id = stripe_session.payment_intent
            payment_method = 'Stripe'
            status = stripe_session.status
            payment = save_payment_infos(request.user, transaction_id, payment_method, order.total, status)

            # update the order model
            order = add_payment_to_order(order, payment)

            # move the cart items to ordered food model
            cart_items = Cart.objects.filter(user=request.user)
            move_cart_items_to_ordered_food(cart_items, order, payment, request.user)

            # send order confirmation email to the customer
            send_order_confirmation_email_to_customer(request, order)

            # send order received email to the vendor
            send_order_received_email_to_vendor(request, cart_items, order)

            # clear the cart if the payment is success
            cart_items.delete()
            
            return redirect(reverse('order-complete')+f'?order_no={order_number}&trans_id={transaction_id}')
        except Exception as e:
            # print(e)
            messages.error(request, 'Something went wrong. Try later.')
            return redirect('cart')
    else:
        # paymentIntent = stripe.PaymentIntent.retrieve(stripe_session.payment_intent)
        # print("stripe_session ==> ",stripe_session)
        # print("payment intent ==> ",paymentIntent)
        messages.error(request, 'Your payment has not been completed. Try again.')
        return redirect('cart')
