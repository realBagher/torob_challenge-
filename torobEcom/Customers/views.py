from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import login, authenticate
from Core.otp_utils import generate_otp, verify_otp  # Import OTP utils from Core
from Core.emails_utils import send_otp_email  # Import email utils from Core
from .forms import LoginForm
from .models import Customer
from django.shortcuts import render
from .forms import CustomerRegistrationForm, AddressFormSet
from django.views.generic import CreateView
from Core.forms import OTPVerificationForm


class RequestOTPView(FormView):
    template_name = "customers/request_otp.html"
    success_url = reverse_lazy("customers:login")

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        try:
            user = Customer.objects.get(email=email)

            otp_code = generate_otp(user)

            send_otp_email(user, otp_code)

            return redirect(self.success_url)
        except Customer.DoesNotExist:
            return render(
                request, self.template_name, {"error": "Email not registered."}
            )


class LoginView(FormView):
    form_class = LoginForm
    template_name = "customers/login.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        otp = form.cleaned_data.get("otp")

        # First, try to authenticate using username and password
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)

        # If password is not provided or authentication fails, try OTP login
        if otp:
            try:
                user = Customer.objects.get(username=username)
                if verify_otp(user, otp):  # Verify OTP using Core utility
                    login(self.request, user)
                    return super().form_valid(form)
                else:
                    form.add_error("otp", "Invalid OTP")
            except Customer.DoesNotExist:
                form.add_error("username", "User does not exist.")

        return self.form_invalid(form)


class CustomerRegistrationView(CreateView):
    model = Customer

    form_class = CustomerRegistrationForm
    template_name = "Core/sign-up.html"
    success_url = "/"

    def get(self, request, *args, **kwargs):
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
            )  # Handle password saving
            customer.save()

            # Link addresses to customer
            address_formset.instance = customer
            address_formset.save()

            return redirect(self.success_url)
        else:
            return render(
                request,
                self.template_name,
                {"customer_form": customer_form, "address_formset": address_formset},
            )


class VerifyOTPAndLoginView(FormView):
    template_name = "customers/verify_otp_login.html"
    form_class = OTPVerificationForm
    success_url = reverse_lazy("home")  # Redirect to home page after successful login

    def form_valid(self, form):
        # Retrieve the email from session (set when sending OTP)
        email = self.request.session.get("email")

        if not email:
            # If no email in session, redirect to login page
            return redirect("login")

        otp = form.cleaned_data.get("otp")

        # Verify the OTP using the core OTP utility
        if verify_otp(email, otp):  # If OTP is correct
            try:
                # Fetch the user using the email
                user = Customer.objects.get(email=email)

                # Log the user in
                login(self.request, user)

                # Redirect to the success URL (e.g., homepage)
                return super().form_valid(form)

            except Customer.DoesNotExist:
                form.add_error(None, "User not found")
                return self.form_invalid(form)
        else:
            # Add error to form if OTP is invalid
            form.add_error("otp", "Invalid OTP")
