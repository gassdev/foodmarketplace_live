from django import forms
from .models import Category, FoodItem
from accounts.validators import allow_only_images_validator


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        

class FoodItemForm(forms.ModelForm):
    class Meta:
        image = forms.FileField(validators=[allow_only_images_validator])
        model = FoodItem
        fields = ['category', 'food_title', 'description', 
                'price', 'image', 'is_available']