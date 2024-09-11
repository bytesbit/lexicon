from django.db import models
from django.utils.translation import gettext_lazy as _

from lexicon.db.models.base import DefaultFieldsModel
from lexicon.db.models.utils import sane_repr, sane_str


class Subtitle(DefaultFieldsModel):
    """
    Subtitle model to store information like video, language, and extracted subtitles with timing information.
    """

    video = models.ForeignKey(
        "lexicon.Video", on_delete=models.CASCADE, db_index=True, verbose_name=_("video")
    )
    language = models.CharField(max_length=50, db_index=True, verbose_name=_("language"))
    cc_subtitle = models.TextField(max_length=1024, db_index=True, verbose_name=_("CC subtitle"))
    start_time = models.TimeField(db_index=True, verbose_name=_("Start time"))
    end_time = models.TimeField(db_index=True, verbose_name=_("End time"))

    class Meta:
        app_label = "lexicon"
        db_table = "lexicon_subtitle"
        verbose_name = _("subtitle")
        verbose_name_plural = _("subtitles")
        ordering = ["-created_at"]

    __repr__ = sane_repr("id")
    __str__ = sane_str("id")
