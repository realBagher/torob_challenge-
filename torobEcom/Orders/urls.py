# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('apply-discount/', views.apply_discount_code, name='apply_discount_code'),
    path('finalize-order/', views.finalize_order, name='finalize_order'),
    path('transfer-cart/', views.transfer_session_cart_to_user, name='transfer_cart'),
]

