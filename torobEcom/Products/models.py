from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.deconstruct import deconstructible
from PIL import Image
import os


class ImageOrSVGValidator:
    def __call__(self, file):
        ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".svg"]
        if ext not in valid_extensions:
            raise ValidationError("Unsupported file extension.")

        # Check file type if it's not SVG
        if ext != ".svg":
            try:
                img = Image.open(file)
                img.verify()  # This will throw an exception if it's not a valid image
            except (IOError, SyntaxError):
                raise ValidationError("Unsupported image file or corrupted image.")


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subcategories",
        blank=True,
        null=True,
    )
    image = models.FileField(
        upload_to="media/category_images/",
        validators=[ImageOrSVGValidator()],
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    def is_subcategory(self):
        return self.parent_category is not None


class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="media/product_images/")

    def __str__(self):
        return f"Image for {self.product.name}"


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="discounts"
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentage or Fixed amount"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.discount_type} discount on {self.product.name}"


class Gift(models.Model):
    code = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gifts")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Gift Code: {self.code} for {self.product.name}"
