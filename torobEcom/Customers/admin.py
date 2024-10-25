from django.contrib import admin
from .models import Customer, Address


admin.site.register(Address)


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    can_delete = True
    fields = [
        "street",
        "city",
        "postal_code",
        "country",
    ]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "username",
        "phone_number",
        "is_active",
    )
    search_fields = ("email", "username", "phone_number")
    list_filter = ("is_active", "is_staff")
    ordering = ("email",)

    inlines = [AddressInline]
