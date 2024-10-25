from django import forms
from .models import Customer, Address
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomerRegistrationForm, AddressFormSet


class CustomerRegistrationView(CreateView):
    model = Customer
    form_class = CustomerRegistrationForm
    template_name = "customers/register.html"
    success_url = reverse_lazy("home")

    def get(self, request, *args, **kwargs):
        # Initialize customer registration form and address formset
        customer_form = self.form_class()
        address_formset = AddressFormSet()
        return render(
            request,
            self.template_name,
            {"customer_form": customer_form, "address_formset": address_formset},
        )

    def post(self, request, *args, **kwargs):
        customer_form = self.form_class(request.POST)
        address_formset = AddressFormSet(request.POST)

        if customer_form.is_valid() and address_formset.is_valid():
            customer = customer_form.save(commit=False)
            customer.set_password(
                customer_form.cleaned_data["password1"]
            )  # Set the password
            customer.save()

            # Save addresses
            address_formset.instance = customer
            address_formset.save()

            login(request, customer)  # Log the user in after successful registration
            return redirect(self.success_url)
        else:
            return


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    otp = forms.CharField(max_length=6, required=False)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["street", "city", "postal_code", "country"]
