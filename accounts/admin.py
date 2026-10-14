"""Django admin configuration for the custom user model."""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AdminUserChangeForm, AdminUserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for creating, updating, and managing user accounts."""

    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    add_form_template = "admin/change_form.html"

    list_display = [
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_locked",
        "last_login",
    ]
    list_filter = ["role", "is_active", "is_locked", "is_superuser"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    readonly_fields = ["last_login", "date_joined", "locked_at"]
    actions = ["unlock_accounts"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "job_title")}),
        ("Access", {"fields": ("role", "is_active", "is_superuser")}),
        ("Lock", {"fields": ("is_locked", "failed_login_attempts", "locked_at")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "job_title", "role"),
            },
        ),
    )

    @admin.action(description="Unlock selected accounts")
    def unlock_accounts(self, request, queryset):
        """Unlock all selected user accounts that are currently locked."""
        locked = queryset.filter(is_locked=True)
        count = locked.count()

        for user in locked:
            user.unlock()

        self.message_user(request, f"{count} account(s) unlocked.", messages.SUCCESS)
