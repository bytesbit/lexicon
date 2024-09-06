from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _

from lexicon.db.models.utils import sane_repr, sane_str


class User(AbstractUser):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("status"),
    )
    email = models.EmailField(
        blank=True, validators=[validate_email], verbose_name=_("email address")
    )
    email_verified = models.BooleanField(default=False, verbose_name=_("email verified"))
    mobile = models.CharField(
        max_length=18, null=True, blank=True, unique=True, verbose_name=_("mobile number")
    )
    mobile_verified = models.BooleanField(default=False, verbose_name=_("mobile verified"))
    avatar_url = models.URLField(max_length=1024, blank=True, verbose_name=_("avatar URL"))
    last_password_change_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("date of last password change"),
        help_text=_("The date and time when the password was last changed."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_("created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, verbose_name=_("last updated at")
    )
    updated_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("updated by"),
    )

    class Meta:
        app_label = "lexicon"
        db_table = "lexicon_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    __repr__ = sane_repr("id", "username")
    __str__ = sane_str("id", "username")

    def save(self, *args, **kwargs):
        """Override save method to normalize email and set username."""
        self.email = self.normalize_email(self.email)

        if not self.username:
            # Set username to email if not set
            self.username = self.email

        super().save(*args, **kwargs)

    @classmethod
    def normalize_email(cls, email):
        """Normalize the email to lowercase and strip whitespace."""
        email = cls.objects.normalize_email(email)
        return email.strip().lower()
