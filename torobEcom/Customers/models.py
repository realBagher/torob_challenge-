from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Custom Manager for Customer
class CustomerManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)


# Custom User Model
class Customer(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)  # Ensure email is unique for OTP
    is_verified = models.BooleanField(default=False)

    objects = CustomerManager()
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_set',  # Custom related name for Customer model
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_permission_set',  # Custom related name for Customer model
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


# Model for Address (Customer can have multiple addresses)
class Address(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="addresses"
    )
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}"
