from django.urls import path
from django.views.generic import TemplateView


app_name = "Core"  # This sets the namespace for the Core app

# Views for different templates like index, partials, etc.
urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("logout", TemplateView.as_view(template_name="index.html"), name="logout"),
    path("signin", TemplateView.as_view(template_name="sign-in.html"), name="sign-in"),
    path("signup", TemplateView.as_view(template_name="sign-up.html"), name="sign-up"),
]
