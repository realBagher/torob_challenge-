# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("view-cart/", views.cart_view, name="view-cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart_view"),
    path(
        "remove-from-cart/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path(
        "remove-from-cart-view/<int:product_id>/",
        views.remove_from_cart_view,
        name="remove_from_cart_view",
    ),
    path(
        "decrease-quantity/<int:product_id>/",
        views.decrease_quantity,
        name="decrease_quantity",
    ),
    path(
        "increase_quantity/<int:product_id>/",
        views.increase_quantity,
        name="increase_quantity",
    ),
    path("apply-discount/", views.apply_discount_code, name="apply_discount_code"),
    path("finalize-order/", views.finalize_order, name="finalize_order"),
    path("transfer-cart/", views.transfer_session_cart_to_user, name="transfer_cart"),
]
