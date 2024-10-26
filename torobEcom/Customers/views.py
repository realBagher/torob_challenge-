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
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.views.generic import FormView
from .forms import LoginForm
from Core.forms import OTPEmailForm
from django_redis import get_redis_connection

import os


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
    template_name = "Core/sign-in.html"
    form_class = LoginForm
    success_url = reverse_lazy("Core:index")

    def form_valid(self, form):
        """
        This method is called when valid form data has been posted.
        It handles user authentication.
        """
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, "You have successfully logged in.")
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid username or password.")
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
            messages.success(request, "ثبت‌نام با موفقیت انجام شد.")
            return redirect(self.success_url)
        else:
            messages.error(request, "خطایی در اطلاعات وارد شده وجود دارد.")
            return render(
                request,
                self.template_name,
                {"customer_form": customer_form, "address_formset": address_formset},
            )


class VerifyOTPAndLoginView(FormView):
    template_name = "Core/otp_login.html"
    form_class = OTPVerificationForm
    success_url = reverse_lazy(
        "Core:index"
    )  # Redirect to home page after successful login

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


def send_otp_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = Customer.objects.get(email=email)
            otp = generate_otp(user.id)  # Generate and store OTP in Redis
            print("\n\n\n\n opt code is:", otp)
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}. It is valid for 5 minutes.",
                os.getenv("__EMAIL_HOST_USER__"),  # Replace with your email
                [user.email],
                fail_silently=False,
            )
            request.session["email"] = (
                email  # Store email in session for OTP verification
            )
            messages.success(request, "OTP has been sent to your email.")
            return redirect("Core:verify_otp")  # Redirect to the OTP verification page
        except Customer.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect("send_otp")
    form = OTPEmailForm()
    return render(
        request,
        "Core/otp_login.html",
        {
            "form": form,
        },
    )


def verify_otp_view(request):
    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data.get("otp")  # The OTP entered by the user
            email = request.session.get("email")  # The email saved in the session

            try:
                # Retrieve the user based on the email stored in session
                user = Customer.objects.get(email=email)

                # Connect to Redis to retrieve the stored OTP for this specific user
                redis_conn = get_redis_connection("default")
                stored_otp = redis_conn.get(
                    f"otp:{user.id}"
                )  # Retrieve the OTP using the user ID

                if stored_otp and int(stored_otp) == int(otp_code):
                    # OTP is correct for this specific user, proceed with login or further actions
                    messages.success(request, "OTP verified successfully.")
                    return redirect(
                        "Core:index"
                    )  # Redirect to the dashboard or home page
                else:
                    # OTP is incorrect or has expired
                    messages.error(request, "Invalid OTP. Please try again.")
                    return redirect("Core:login")
            except Customer.DoesNotExist:
                messages.error(request, "An error occurred. Please try again.")
                return redirect("Core:otp_login")
    else:
        form = OTPVerificationForm()

    return render(request, "Core/verify_otp.html", {"form": form})
