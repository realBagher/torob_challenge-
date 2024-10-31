from Products.models import Category, Product
from Orders.models import Order
from django.shortcuts import render
from django.shortcuts import get_object_or_404


def index_view(request):
    """
    Function-based view to render the index.html page with categories, cart items, total amount, and total count.
    """
    categories = Category.objects.all()
    products = Product.objects.all()

    cart_items = []
    total_amount = 0
    total_count = 0

    if request.user.is_authenticated:

        order = Order.objects.filter(customer=request.user, status="cart").first()
        if order:

            for item in order.items.select_related("product").all():
                product_total = item.product.price * item.quantity
                total_amount += product_total  # Accumulate total amount
                total_count += item.quantity  # Accumulate total count of items
                cart_items.append(
                    {
                        "id": item.product.id,
                        "name": item.product.name,
                        "price": item.product.price,
                        "quantity": item.quantity,
                        "image_url": item.product.image.url,
                        "total_price": int(product_total),  # Convert to integer
                    }
                )
    else:
        # For guest users, get the item data from the session cart
        cart = request.session.get("cart", {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            product_total = product.price * quantity
            total_amount += product_total  # Accumulate total amount
            total_count += quantity  # Accumulate total count of items
            cart_items.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "quantity": quantity,
                    "image_url": product.image.url,
                    "total_price": int(product_total),  # Convert to integer
                }
            )

    # Convert total_amount to integer before passing to the template
    total_amount = int(total_amount)

    return render(
        request,
        "index.html",
        {
            "categories": categories,
            "products": products,
            "total_amount": total_amount,
            "total_count": total_count,
            "cart_items": cart_items,
        },
    )
