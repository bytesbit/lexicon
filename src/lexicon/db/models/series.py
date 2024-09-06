from django.db import models
from django.utils.crypto import get_random_string

DEFAULT_RANDOM_CHARS_PLACEHOLDER = "XXXX"


def generate_random_number(length=4):
    return get_random_string(length=length, allowed_chars="0123456789")


def generate_series_next(pattern: str, length=4, placeholder=None):
    placeholder = placeholder or DEFAULT_RANDOM_CHARS_PLACEHOLDER
    return pattern.replace(placeholder, generate_random_number(length))


class SeriesField(models.CharField):
    def __init__(self, *args, **kwargs):
        self._pattern = kwargs.pop("pattern", None)
        self.random_length = kwargs.pop("random_length", None)
        self.placeholder = kwargs.pop("placeholder", DEFAULT_RANDOM_CHARS_PLACEHOLDER)
        models.CharField.__init__(self, *args, **kwargs)

    def get_pattern(self, obj):
        if callable(self._pattern):
            pattern = self._pattern(obj)
        else:
            pattern = self._pattern
        return pattern

    def get_series_next(self, obj):
        pattern = self.get_pattern(obj)
        return generate_series_next(
            pattern, length=self.random_length, placeholder=self.placeholder
        )


class SeriesModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._set_series_fields()
        super().save(*args, **kwargs)

    def _set_series_fields(self):
        for f in self._meta.concrete_fields:
            if not isinstance(f, SeriesField):
                # ignore non-series fields
                continue

            fvalue = getattr(self, f.attname)
            if fvalue:
                # ignore if series field's value already exist
                continue

            value = f.get_series_next(self)
            setattr(self, f.attname, value)
