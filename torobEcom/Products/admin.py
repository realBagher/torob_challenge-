from django.contrib import admin

from django.contrib import admin
from .models import Category, Brand, Product, Discount, Gift, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Allows adding one extra image by default
    fields = ["image"]
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"


class GiftInline(admin.TabularInline):
    model = Gift
    extra = 1
    fields = ["code", "active"]
    verbose_name = "Gift Code"
    verbose_name_plural = "Gift Codes"


class DiscountInline(admin.TabularInline):
    model = Discount
    extra = 1
    fields = ["discount_type", "amount", "active"]
    verbose_name = "Discount"
    verbose_name_plural = "Discounts"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "brand", "stock"]
    inlines = [ProductImageInline, GiftInline, DiscountInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent_category"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin.site.register(ProductImage)
admin.site.register(Gift)
admin.site.register(Discount)
