from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.utils.deconstruct import deconstructible
from PIL import Image
import os


@deconstructible
class ImageOrSVGValidator:
    def __call__(self, file):
        ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".svg"]
        if ext not in valid_extensions:
            raise ValidationError("Unsupported file extension.")

        if ext != ".svg":
            try:
                img = Image.open(file)
                img.verify()
            except (IOError, SyntaxError):
                raise ValidationError("Unsupported image file or corrupted image.")


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
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
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def is_subcategory(self):
        return self.parent_category is not None


class Brand(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Brand, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="Product")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    stock = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50"/>' % (self.image.url))


class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(upload_to="product-images")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Product Images"


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="discounts"
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentage or Fixed amount"
    )
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.discount_type}-{self.product.name}")
        super(Discount, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.discount_type} discount on {self.product.name}"


class Gift(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gifts")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code)
        super(Gift, self).save(*args, **kwargs)

    def __str__(self):
        return f"Gift Code: {self.code} for {self.product.name}"
