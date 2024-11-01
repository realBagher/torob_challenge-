from django.contrib import admin
from .models import Customer, Address
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.template.response import TemplateResponse
from django.urls import path


admin.site.register(Address)
from django.shortcuts import redirect, get_object_or_404


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
    list_display = ("email", "username", "phone_number", "is_active")
    change_password_form = AdminPasswordChangeForm
    search_fields = ("email", "username", "phone_number")
    list_filter = ("is_active", "is_staff")
    ordering = ("email",)
    inlines = [AddressInline]

    # Custom URL for changing password
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<id>/change-password/",
                self.admin_site.admin_view(self.change_password),
                name="customer_change_password",
            ),
        ]
        return custom_urls + urls

    # Password change method
    def change_password(self, request, id, form_url=""):
        customer = get_object_or_404(Customer, pk=id)  # Ensure customer is found

        if request.method == "POST":
            form = self.change_password_form(customer, request.POST)
            if form.is_valid():
                form.save()
                return redirect(
                    "admin:your_app_name_customer_changelist"
                )  # Redirect after password change
        else:
            form = self.change_password_form(customer)

        context = {
            **self.admin_site.each_context(request),
            "title": f"Change password for {customer.username}",
            "form": form,
            "is_popup": False,
            "add": False,
            "change": True,
            "has_view_permission": True,
            "has_add_permission": False,
            "has_change_permission": True,
            "has_delete_permission": False,
            "save_as": False,
            "show_save": True,
        }

        return TemplateResponse(
            request,
            "admin/auth/user/change_password.html",
            context,
        )

    # Method to add a custom button/link to the admin detail view for each user
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_change_password"] = (
            True  # Flag to show password change link
        )
        extra_context["password_change_url"] = f"{object_id}/change-password/"
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )
