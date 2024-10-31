from django.urls import path
from django.views.generic import TemplateView
from Core.views import index_view
from Customers.views import (
    CustomerRegistrationView,
    LoginView,
    send_otp_view,
    verify_otp_view,
    logout_view,
)
from Products.views import category_list

app_name = "Core"  


urlpatterns = [
    path("", index_view, name="index"),
    path("signup", CustomerRegistrationView.as_view(), name="sign-up"),
    path("login", LoginView.as_view(), name="login"),
    path("otp-login/", send_otp_view, name="otp-login"),
    path("verify_otp/", verify_otp_view, name="verify_otp"),
    path("logout/", logout_view, name="logout"),
]
