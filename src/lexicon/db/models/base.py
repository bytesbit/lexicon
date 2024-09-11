from typing import List, Union

from django.contrib.auth import get_user_model
from django.db import connection, models
from django.utils.translation import gettext_lazy as _

from lexicon.db.models.utils import sane_repr, sane_str

__all__ = [
    "BaseModel",
    "Model",
    "TimeStampedModel",
    "DefaultFieldsModel",
]


class BaseModel(models.Model):
    """
    An abstract base model providing methods to track changes in model fields.
    """

    class Meta:
        abstract = True

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Create an instance from database values, marking it as not being newly added.

        Args:
            cls (Type[BaseModel]): The class of the model.
            db (str): The database alias.
            field_names (list of str): List of field names.
            values (list): List of field values corresponding to `field_names`.

        Returns:
            BaseModel: An instance of the model with its state updated.
        """
        instance = super().from_db(db, field_names, values)
        instance._state.adding = False
        instance._state.db = db
        instance._old_values = dict(zip(field_names, values))
        return instance

    def data_changed(self, fields: List[str]) -> bool:
        """
        Check if any of the specified fields have changed since the instance was created.

        Args:
            fields (List[str]): List of field names to check.

        Returns:
            bool: True if any of the fields have changed, otherwise False.
        """
        if hasattr(self, "_old_values"):
            if not self.pk or not self._old_values:
                return True

            for field in fields:
                if getattr(self, field) != self._old_values.get(field):
                    return True
            return False

        return True


class Model(BaseModel):
    """
    An abstract model with a method to truncate the associated database table.
    """

    class Meta:
        abstract = True

    __repr__ = sane_repr("id")
    __str__ = sane_str("id")

    @classmethod
    def truncate(cls):
        """
        Delete all data from the model's table using a single query.

        This method efficiently truncates the table and cascades the delete to related tables.
        """
        with connection.cursor() as cursor:
            cursor.execute(f'TRUNCATE TABLE "{cls._meta.db_table}" CASCADE')


class TimeStampedModel(Model):
    """
    An abstract model that includes fields to track creation and last modification times.
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
    """
    An abstract model that includes default fields for tracking creation and modification
    user information.
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
        """
        Override the save method to set the 'created_by' and 'updated_by' fields based on the
        current user. Only set 'created_by' if the instance is new.

        Args:
            *args: Positional arguments passed to the parent save method.
            **kwargs: Keyword arguments passed to the parent save method.
        """
        from lexicon.middleware.current_user import get_current_user

        user = get_current_user()
        if user and user.is_authenticated:
            if self._state.adding:
                self.created_by = user
            self.updated_by = user

            # Append updated fields to `update_fields` if specified
            self.append_to_update_fields(["updated_by", "created_by"], **kwargs)

        super().save(*args, **kwargs)

    def append_to_update_fields(self, fields: Union[List[str], str], update_fields=None, **kwargs):
        """
        Add the specified fields to the `update_fields` list if it exists, to ensure they are
        included in the save operation.

        Args:
            fields (Union[List[str], str]): Field names to be added to the update fields.
            update_fields (list, optional): Existing list of fields to be updated.
            **kwargs: Additional keyword arguments.
        """
        if isinstance(fields, str):
            fields = [fields]

        if update_fields is not None:
            update_fields.extend(f for f in fields if f not in update_fields)
