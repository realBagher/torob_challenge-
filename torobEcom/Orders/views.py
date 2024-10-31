from django.shortcuts import render

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from Products.models import Product


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem, Product


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get("quantity", 1))

    if request.user.is_authenticated:

        order, created = Order.objects.get_or_create(
            customer=request.user, status="cart"
        )

        item, item_created = OrderItem.objects.get_or_create(
            order=order, product=product
        )

        if not item_created:
            item.quantity += quantity
        else:

            item.quantity = quantity
        item.save()
    else:

        cart = request.session.get("cart", {})

        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:

            cart[str(product_id)] = quantity

        request.session["cart"] = cart

    messages.success(request, f"{product.name} added to cart.")
    return redirect("Core:index")


def cart_view(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(
            customer=request.user, status="cart"
        )
    else:
        order = None
        cart = request.session.get("cart", {})
        products = Product.objects.filter(id__in=cart.keys())
        cart_items = [
            {"product": product, "quantity": cart[str(product.id)]}
            for product in products
        ]

    return render(
        request,
        "cart.html",
        {"order": order, "cart_items": cart_items if not order else order.items.all()},
    )


def apply_discount_code(request):
    code = request.POST.get("discount_code")
    if request.user.is_authenticated:
        order = Order.objects.get(customer=request.user, status="cart")

        if code == "DISCOUNT10":
            order.discount_amount = 10
            order.discount_code = code
            order.save()
            messages.success(request, "Discount code applied.")
        else:
            messages.error(request, "Invalid discount code.")
    else:
        messages.error(request, "You must be logged in to apply a discount code.")
    return redirect("cart_view")


@login_required
def finalize_order(request):
    order = Order.objects.get(customer=request.user, status="cart")
    if order.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("cart_view")

    # Mark the order as finalized
    order.status = "order"
    order.save()
    messages.success(request, "Order finalized successfully.")
    return redirect("order_summary", order_id=order.id)


def transfer_session_cart_to_user(request):
    cart = request.session.get("cart", {})
    if cart and request.user.is_authenticated:
        order, created = Order.objects.get_or_create(
            customer=request.user, status="cart"
        )
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            item, item_created = OrderItem.objects.get_or_create(
                order=order, product=product
            )
            item.quantity += quantity
            item.save()
        del request.session["cart"]
    return redirect("cart_view")
