from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    parent_category = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="subcategories",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    @property
    def has_subcategories(self):
        """Check if the category has any subcategories."""
        return self.subcategories.exists()


class Discount(models.Model):
    DISCOUNT_TYPES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.discount_type} - {self.value}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    discount = models.ForeignKey(
        Discount,
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def price_after_discount(self):
        """Calculate the price after applying the discount if there is one."""
        if self.discount and self.discount.is_active:
            if self.discount.discount_type == "percentage":
                return self.price - (self.price * self.discount.value / 100)
            elif self.discount.discount_type == "fixed":
                return max(self.price - self.discount.value, 0)
        return self.price
