from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer


class CustomerRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = Customer
        fields = ["username", "phone_number", "password1", "password2"]


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True)
