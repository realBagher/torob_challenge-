from django.db import models
from Customers.models import Customer


from django.db import models
from django.contrib.auth.models import User
from Products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Cart'),
        ('order', 'Order')
    ]

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount_code = models.CharField(max_length=20, blank=True, null=True)  # Optional discount code

    def __str__(self):
        return f"Order {self.id} - {self.customer if self.customer else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
