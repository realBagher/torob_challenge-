from Products.models import Category, Product
from django.shortcuts import render


def index_view(request):
    """
    Function-based view to render the index.html page with categories.
    """

    categories = Category.objects.all()
    products = Product.objects.all()

    print(products[0].image.url)

    return render(
        request, "index.html", {"categories": categories, "products": products}
    )
