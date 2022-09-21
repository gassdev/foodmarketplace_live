import datetime
import simplejson as json
from django.contrib.sites.shortcuts import get_current_site

from accounts.utils import send_notification
from vendor.models import Vendor

from .models import OrderedFood, Payment

def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number

def save_payment_infos(user, transaction_id, payment_method, amount, status):
    payment = Payment.objects.create(
        user=user,
        transaction_id=transaction_id,
        payment_method=payment_method,
        amount=amount,
        status=status
    )
    payment.save()
    return payment

def add_payment_to_order(order, payment):
    order.payment = payment
    order.is_ordered = True
    order.save()
    return order

def move_cart_items_to_ordered_food(cart_items, order, payment, user):
    for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity # total amount
            ordered_food.save()

def send_order_confirmation_email_to_customer(request, order):
    mail_subject = 'Thank you for ordering with us'
    email_template = 'orders/order_confirmation_email.html'

    ordered_food = OrderedFood.objects.filter(order=order)
    customer_subtotal = 0
    for item in ordered_food:
        customer_subtotal += item.price * item.quantity
    tax_data = json.loads(order.tax_data)
    context = {
        'user': request.user,
        'order': order,
        'to_email': order.email,
        'ordered_food': ordered_food,
        'domain': get_current_site(request),
        'customer_subtotal': customer_subtotal,
        'tax_data': tax_data,
    }
    send_notification(mail_subject, email_template, context)

def send_order_received_email_to_vendor(request, cart_items, order):
    mail_subject = 'You have received a new order'
    email_template = 'orders/new_order_received.html'
    to_emails = []
    for i in cart_items:
        if i.fooditem.vendor.user.email not in to_emails:
            to_emails.append(i.fooditem.vendor.user.email)

            ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.fooditem.vendor)
            # print(ordered_food_to_vendor)

            context = {
                'order': order,
                'vendor_name':i.fooditem.vendor.vendor_name,
                'to_email': i.fooditem.vendor.user.email,
                'ordered_food_to_vendor': ordered_food_to_vendor,
                'domain': get_current_site(request),
                'vendor_subtotal': get_order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'],
                'tax_data': get_order_total_by_vendor(order, i.fooditem.vendor.id)['tax_dict'],
                'vendor_grand_total': get_order_total_by_vendor(order, i.fooditem.vendor.id)['grand_total'],
            }
            send_notification(mail_subject, email_template, context)

def get_order_total_by_vendor(order, vendor_id):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    subtotal = 0
    tax = 0
    tax_dict = {}
        
    for key, val in data.items():
        subtotal += float(key)
        val = val.replace("'",'"')
        val = json.loads(val)
        tax_dict.update(val)

        # calculate tax
        # {'TVA': {'8.00': '672'}}
        for i in val:
            for j in val[i]:
                tax += float(val[i][j])

    grand_total = float(subtotal) + float(tax)
    
    context = {
        'subtotal': subtotal,
        'tax_dict': tax_dict,
        'grand_total': grand_total,
    }
    return context
