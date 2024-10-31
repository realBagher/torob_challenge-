from django.urls import path
from . import views

app_name = "Products"

urlpatterns = [
    path("", views.category_list, name="category-list"),
    path(
        "categories/<int:cid>/",
        views.category_product_list,
        name="category-product-list",
    ),
]
