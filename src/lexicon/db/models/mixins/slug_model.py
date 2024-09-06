from django.core import checks
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField


class SlugModelMixin(models.Model):
    slug = AutoSlugField(
        populate_from="get_slug_field",
        unique=True,
        editable=False,
        verbose_name=_("slug"),
    )

    # a field name from which slug will be populated
    SLUG_POPULATE_FROM = None

    class Meta:
        abstract = True

    def get_slug_field(self):
        return getattr(self, self.SLUG_POPULATE_FROM)

    def slugify_function(self, content):
        """Super class can override this method, to customize slugify function"""
        return slugify(content)

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        errors += [*cls._check_slug_populate_from()]
        return errors

    @classmethod
    def _check_slug_populate_from(cls):
        if not cls.SLUG_POPULATE_FROM:
            return [
                checks.Error(
                    "'SLUG_POPULATE_FROM' must be set, found None or empty " "string.",
                    obj=cls,
                )
            ]
        return []
