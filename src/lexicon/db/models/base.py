from typing import List, Union

from django.contrib.auth import get_user_model
from django.db import connection, models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import UUIDField

from lexicon.db.models.utils import sane_repr, sane_str

__all__ = [
    "BaseModel",
    "Model",
    "UUIDModel",
    "TimeStampedModel",
    "DefaultFieldsModel",
]


class BaseModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._state.adding = False
        instance._state.db = db
        instance._old_values = dict(zip(field_names, values))
        return instance

    def data_changed(self, fields):
        """
        example:
        if self.data_changed(['street', 'street_no', 'zip_code', 'city',
        'country']):
            print("one of the fields changed")

        returns true if the model saved the first time and _old_values
        doesn't exist

        :param fields:
        :return:
        """
        if hasattr(self, "_old_values"):
            if not self.pk or not self._old_values:
                return True

            for field in fields:
                if getattr(self, field) != self._old_values[field]:
                    return True
            return False

        return True


class Model(BaseModel):
    """
    An abstract model
    """

    class Meta:
        abstract = True

    __repr__ = sane_repr("id")
    __str__ = sane_str("id")

    @classmethod
    def truncate(cls):
        """Delete all data in table but efficiently in single query"""
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(cls._meta.db_table))


class UUIDModel(Model):
    """An abstract model having id/pk as UUID field.

    Mostly, we prefer UUID based pk/id field for public facing resource and
    for which we want pk value obscure due to security reasons.
    """

    id = UUIDField(verbose_name=_("id"))

    class Meta:
        abstract = True


class TimeStampedModel(Model):
    """Fields which stores model instance creation time and last
    modification time
    """

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_("created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, verbose_name=_("last updated at")
    )

    class Meta:
        abstract = True


class DefaultFieldsModel(TimeStampedModel):
    """Our default fields model for all custom model we write in this project.

    Also, stores user who created this instance and who updated it last
    time.
    """

    created_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        editable=False,
        related_name="%(class)s_created",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        editable=False,
        related_name="%(class)s_updated",
        verbose_name=_("last updated by"),
    )

    class Meta(TimeStampedModel.Meta):
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        from lexicon.middleware.current_user import get_current_user

        user = get_current_user()
        if user and user.is_authenticated:
            self.updated_by = user
            self.append_to_update_fields(["updated_by"], **kwargs)
            if self._state.adding:
                self.created_by = user
                self.append_to_update_fields(["created_by"], **kwargs)

        super().save(*args, **kwargs)

    def append_to_update_fields(self, fields: Union[List[str], str], update_fields=None, **kwargs):
        """
        Append given fields to update_fields list if exists otherwise ignore it. This we can use
        inside `.save()` model method to make model fields update consistent if `update_fields` is
        set in `.save()` arguments.
        """
        if isinstance(fields, str):
            fields = [fields]

        if update_fields:
            [update_fields.append(f) for f in fields]
