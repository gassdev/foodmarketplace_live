from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['last_name', 'first_name', 'phone', 
                'email', 'address', 'country', 'state', 'city', 'pin_code']