# Generated by Django 4.2.16 on 2024-10-19 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("Customers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("product_name", models.CharField(max_length=255)),
                (
                    "order_status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Shipped", "Shipped"),
                            ("Delivered", "Delivered"),
                        ],
                        max_length=50,
                    ),
                ),
                ("order_date", models.DateTimeField(auto_now_add=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to="Customers.customer",
                    ),
                ),
            ],
        ),
    ]
