from django.urls import path
from django.views.generic import TemplateView
from Customers.views import (
    CustomerRegistrationView,
    LoginView,
    send_otp_view,
    verify_otp_view,
    logout_view,
)


app_name = "Core"  # This sets the namespace for the Core app

# Views for different templates like index, partials, etc.
urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("signup", CustomerRegistrationView.as_view(), name="sign-up"),
    path("login", LoginView.as_view(), name="login"),
    path("otp-login/", send_otp_view, name="otp-login"),
    path("verify_otp/", verify_otp_view, name="verify_otp"),
    path("logout/", logout_view, name="logout"),
]
