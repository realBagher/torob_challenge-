from django import forms
from .models import Customer, Address
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django import forms
from django.forms import inlineformset_factory


class CustomerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    password2 = forms.CharField(widget=forms.PasswordInput, label="تایید رمز عبور")

    class Meta:
        model = Customer
        fields = ["username", "phone_number", "email", "password1", "password2"]
        labels = {
            "username": "نام کاربری",
            "phone_number": "شماره تلفن",
            "email": "ایمیل",
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return cleaned_data


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["street", "city", "postal_code", "country"]
        labels = {
            "street": "خیابان",
            "city": "شهر",
            "postal_code": "کد پستی",
            "country": "کشور",
        }


# Inline formset to handle multiple addresses for a single customer
AddressFormSet = inlineformset_factory(
    Customer, Address, form=AddressForm, extra=1, can_delete=True
)


class LoginForm(forms.Form):
    username = forms.CharField(label="نام کاربری")
    password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="رمز عبور"
    )
