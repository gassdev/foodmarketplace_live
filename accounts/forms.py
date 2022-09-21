from django import forms
from .models import User, UserProfile
from .validators import allow_only_images_validator

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 
                'email', 'password']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError(
                "Password does not match!"
            )


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.FileField(validators=[allow_only_images_validator])
    cover_photo = forms.FileField(validators=[allow_only_images_validator])
    
    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 
                'country', 'state', 'city', 'pin_code', 'latitude', 'longitude']

    
    # def __init__(self, *args, **kwargs):
    #     super(UserProfileForm, self).__init__(*args, **kwargs)
    #     for field in self.fields:
    #         if field == 'latitude' or field == 'longitude':
    #             self.fields[field].widget.attrs['readonly'] = 'readonly'


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']