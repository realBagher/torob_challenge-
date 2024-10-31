from django.shortcuts import render
from .models import Category


def category_list(request):

    categories = Category.objects.all()

    print("\n cat: ", categories)
    return render(request, "partials/base.html", {"categories": categories})


def category_product_list(request, cid):
    category = Category.objects.get(id=cid)
    products = products.objects.filter(category=category)
    return render(
        request,
        "category_product_list.html",
        {"category": category, "products": products},
    )
