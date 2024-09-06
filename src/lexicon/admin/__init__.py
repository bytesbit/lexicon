from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from lexicon.models import User

DEFAULT_READONLY_FIELDS = (
    "created_by",
    "created_at",
    "updated_at",
    "updated_by",
)


class BaseDefaultModelAdmin(admin.ModelAdmin):
    readonly_fields = DEFAULT_READONLY_FIELDS
    ordering = ("-created_at",)


@admin.register(User)
class UserAdmin(BaseDefaultModelAdmin):

    list_display = (
        "title",
        "email",
        "mobile",
        "mobile_verified",
        "email_verified",
        "date_joined",
    )
    readonly_fields = ("date_joined",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "mobile",
                    "status",
                    "is_active",
                    "mobile_verified",
                    "email_verified",
                    "avatar_url",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "classes": ("collapse",),
                "fields": ("is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
    )
    list_filter = ("is_active", "is_staff")
    search_fields = ("first_name", "last_name", "email", "mobile")

    def title(self, obj):
        return f"User (ID: {obj.id}) - {obj.username}"
