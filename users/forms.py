from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    notification_preference = forms.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')],
        initial='email'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'notification_preference', 'password1', 'password2']
