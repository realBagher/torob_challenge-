from django import forms
from .models import Customer, Address


class CustomerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ["username", "phone_number", "email", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    otp = forms.CharField(max_length=6, required=False)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["street", "city", "postal_code", "country"]
