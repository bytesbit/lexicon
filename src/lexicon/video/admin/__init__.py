from django.contrib import admin

from lexicon.video.models import Video

DEFAULT_READONLY_FIELDS = (
    "created_by",
    "created_at",
    "updated_at",
    "updated_by",
)


class BaseDefaultModelAdmin(admin.ModelAdmin):
    readonly_fields = DEFAULT_READONLY_FIELDS
    ordering = ("-created_at",)


@admin.register(Video)
class VideoAdmin(BaseDefaultModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "created_at",
    )
    list_display_links = ["title"]
