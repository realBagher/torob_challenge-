from django.shortcuts import render

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from Products.models import Product, Discount
from django.http import JsonResponse

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


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:

        order = Order.objects.filter(customer=request.user, status="cart").first()
        if order:
            OrderItem.objects.filter(order=order, product_id=product_id).delete()
    else:

        cart = request.session.get("cart", {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session["cart"] = cart
    messages.success(request, "کالای درخواستی از سبد خرید حذف شد.")
    return redirect("Core:index")


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


def cart_view(request):
    cart_items = []
    total_amount = 0
    if request.user.is_authenticated:
        order = Order.objects.filter(customer=request.user, status="cart").first()
        if order:
            for item in order.items.select_related("product").all():
                product_total = item.product.price * item.quantity
                total_amount += product_total
                cart_items.append(
                    {
                        "id": item.product.id,
                        "name": item.product.name,
                        "price": item.product.price,
                        "quantity": item.quantity,
                        "image_url": item.product.image.url,
                        "total_price": product_total,
                        "rating": item.product.rating,  # Assuming rating is a field on Product
                        "rating_percentage": item.product.rating
                        * 20,  # e.g., for a 5-star system
                    }
                )
    else:
        cart = request.session.get("cart", {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            product_total = product.price * quantity
            total_amount += product_total
            cart_items.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "quantity": quantity,
                    "image_url": product.image.url,
                    "total_price": product_total,
                }
            )

    return render(
        request,
        "cart2.html",
        {
            "cart_items": cart_items,
            "total_amount": total_amount,
        },
    )


def increase_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:

        order, created = Order.objects.get_or_create(
            customer=request.user, status="cart"
        )
        item, item_created = OrderItem.objects.get_or_create(
            order=order, product=product
        )

        item.quantity += 1
        item.save()

        item_total = item.product.price * item.quantity
        cart_total = sum(i.product.price * i.quantity for i in order.items.all())

        return JsonResponse(
            {
                "success": True,
                "quantity": item.quantity,
                "item_total": item_total,
                "cart_total": cart_total,
            }
        )

    else:

        cart = request.session.get("cart", {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session["cart"] = cart

        item_total = product.price * cart[str(product_id)]
        cart_total = sum(
            Product.objects.get(id=int(pid)).price * qty for pid, qty in cart.items()
        )

        return JsonResponse(
            {
                "success": True,
                "quantity": cart[str(product_id)],
                "item_total": item_total,
                "cart_total": cart_total,
            }
        )


def decrease_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        order = Order.objects.filter(customer=request.user, status="cart").first()
        if order:
            item = OrderItem.objects.filter(order=order, product=product).first()
            if item:
                if item.quantity > 1:
                    item.quantity -= 1
                    item.save()
                    item_total = item.product.price * item.quantity
                    cart_total = sum(
                        i.product.price * i.quantity for i in order.items.all()
                    )
                    return JsonResponse(
                        {
                            "success": True,
                            "quantity": item.quantity,
                            "item_total": item_total,
                            "cart_total": cart_total,
                        }
                    )
                else:
                    item.delete()
                    cart_total = sum(
                        i.product.price * i.quantity for i in order.items.all()
                    )
                    return JsonResponse(
                        {
                            "success": True,
                            "quantity": 0,
                            "item_total": 0,
                            "cart_total": cart_total,
                        }
                    )

    else:
        cart = request.session.get("cart", {})
        if str(product_id) in cart:
            if cart[str(product_id)] > 1:
                cart[str(product_id)] -= 1
            else:
                del cart[str(product_id)]

        request.session["cart"] = cart

        item_total = product.price * cart.get(str(product_id), 0)
        cart_total = sum(
            Product.objects.get(id=int(pid)).price * qty for pid, qty in cart.items()
        )
        return JsonResponse(
            {
                "success": True,
                "quantity": cart.get(str(product_id), 0),
                "item_total": item_total,
                "cart_total": cart_total,
            }
        )


# Apply discount code
def apply_discount_code(request):
    code = request.POST.get("discount_code")
    discount = Discount.objects.filter(code=code, active=True).first()
    order = Order.objects.filter(customer=request.user, status="cart").first()

    if discount and order:
        discount_amount = discount.amount
        total_amount = sum(
            item.product.price * item.quantity for item in order.items.all()
        )
        if discount.discount_type == "percentage":
            total_amount -= total_amount * discount.amount / 100
        else:
            total_amount -= discount.amount

        return JsonResponse(
            {
                "success": True,
                "total_amount": total_amount,
                "discount_amount": discount.amount,
            }
        )
    return JsonResponse({"success": False, "message": "Invalid discount code"})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Product


def remove_from_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:

        order = Order.objects.filter(customer=request.user, status="cart").first()
        if order:

            item = OrderItem.objects.filter(order=order, product=product).first()
            if item:
                item.delete()

            cart_total = sum(i.product.price * i.quantity for i in order.items.all())
            return JsonResponse({"success": True, "cart_total": cart_total})

    else:

        cart = request.session.get("cart", {})

        if str(product_id) in cart:
            del cart[str(product_id)]

        request.session["cart"] = cart

        cart_total = sum(
            Product.objects.get(id=int(pid)).price * qty for pid, qty in cart.items()
        )

        return JsonResponse({"success": True, "cart_total": cart_total})

    return JsonResponse({"success": False, "message": "Item not found in cart"})
