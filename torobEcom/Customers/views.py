from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import login, authenticate
from Core.otp_utils import generate_otp, verify_otp  # Import OTP utils from Core
from Core.emails_utils import send_otp_email  # Import email utils from Core
from .forms import LoginForm
from .models import Customer
from django.shortcuts import render
from 

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
