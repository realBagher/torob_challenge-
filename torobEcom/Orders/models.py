from django.db import models
from Customers.models import Customer


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    product_name = models.CharField(max_length=255)
    order_status = models.CharField(
        max_length=50,
        choices=[
            ("Pending", "Pending"),
            ("Shipped", "Shipped"),
            ("Delivered", "Delivered"),
        ],
    )
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for {self.product_name}"
