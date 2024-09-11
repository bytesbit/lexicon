from django.db import models
from django.utils.translation import gettext_lazy as _

from lexicon.db.models.base import DefaultFieldsModel
from lexicon.db.models.utils import sane_repr, sane_str


class Video(DefaultFieldsModel):
    """
    Video model to store information about uploaded videos including title, description,
    and the actual video file. This model extends the DefaultFieldsModel to include
    common fields such as created_at and updated_at timestamps.
    """

    title = models.CharField(
        max_length=255, verbose_name=_("title"), help_text=_("Title of the video")
    )
    description = models.TextField(
        verbose_name=_("description"), help_text=_("Brief description of the video content")
    )
    video_file = models.FileField(
        upload_to="videos/",
        verbose_name=_("video file"),
        help_text=_("Upload video file in MP4, AVI, or MOV format"),
    )

    class Meta:
        app_label = "lexicon"
        db_table = "lexicon_video"
        verbose_name = _("video")
        verbose_name_plural = _("videos")
        ordering = ["-created_at"]

    __repr__ = sane_repr("id", "title")
    __str__ = sane_str("id", "title")

    def get_video_url(self):
        """
        Returns the URL of the video file for display in templates.
        """
        return self.video_file.url if self.video_file else None
