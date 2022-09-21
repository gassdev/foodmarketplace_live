from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import intcomma

from .models import Payment, Order, OrderedFood

class OrderedFoodInline(admin.TabularInline):
    def thumbnail(self, object):
        return format_html(
            f'<img src="{object.fooditem.image.url}" width="40" style="border-radius: 50px;" />'
        )
    thumbnail.short_description = 'Photo'

    def ordered_food_amount(self, object):
        return f"{intcomma(object.amount)} XOF"
    ordered_food_amount.short_description = 'amount'

    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'fooditem', 'thumbnail',
                'quantity', 'price', 'ordered_food_amount')
    exclude = ['amount']
    extra = 0
    can_delete = False

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 
            'email', 'total', 'payment_method', 'status', 'order_placed_to', 'is_ordered']
    inlines = [OrderedFoodInline]
    list_filter = ['is_ordered', 'payment_method']

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)