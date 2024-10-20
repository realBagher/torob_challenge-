from django.urls import path
from django.views.generic import TemplateView

# Views for different templates like index, partials, etc.
urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
]
