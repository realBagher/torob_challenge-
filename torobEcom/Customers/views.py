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

from django.contrib.auth import logout


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
            customer.set_password(customer_form.cleaned_data["password1"])
            customer.save()

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
    success_url = reverse_lazy("Core:index")

    def form_valid(self, form):

        email = self.request.session.get("email")

        if not email:

            return redirect("login")

        otp = form.cleaned_data.get("otp")

        if verify_otp(email, otp):
            try:

                user = Customer.objects.get(email=email)

                login(self.request, user)

                return super().form_valid(form)

            except Customer.DoesNotExist:
                form.add_error(None, "User not found")
                return self.form_invalid(form)
        else:

            form.add_error("otp", "Invalid OTP")


def send_otp_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = Customer.objects.get(email=email)
            otp = generate_otp(user.id)
            print("\n\n\n\n opt code is:", otp)
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}. It is valid for 5 minutes.",
                os.getenv("__EMAIL_HOST_USER__"),
                [user.email],
                fail_silently=False,
            )
            request.session["email"] = email
            messages.success(request, "OTP has been sent to your email.")
            return redirect("Core:verify_otp")
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
            otp_code = form.cleaned_data.get("otp")
            email = request.session.get("email")

            try:

                user = Customer.objects.get(email=email)

                redis_conn = get_redis_connection("default")
                stored_otp = redis_conn.get(f"otp:{user.id}")

                if stored_otp and int(stored_otp) == int(otp_code):

                    messages.success(request, "با کد موقت با موافقیت لاگین کردید")
                    return redirect("Core:index")
                else:

                    messages.error(request, "کد موقت اشتباه است دوباره سعی کنید ")
                    return redirect("Core:login")
            except Customer.DoesNotExist:
                messages.error(request, "مشکلی رخ داده است دوباره سعی کنید.")
                return redirect("Core:otp_login")
    else:
        form = OTPVerificationForm()

    return render(request, "Core/verify_otp.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "با موفقیت خارج شدید")
    return redirect("Core:index")
