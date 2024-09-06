import rest_framework.fields
from django.contrib.auth.password_validation import get_password_validators, validate_password
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import DjangoValidationError, get_error_detail


class BasePasswordField(rest_framework.fields.CharField):
    """Base class for password fields with configurable validation."""

    MIN_LENGTH = 8
    MAX_LENGTH = 50

    def __init__(self, disable_validate_password=False, **kwargs):
        kwargs["max_length"] = self.MAX_LENGTH
        kwargs["allow_blank"] = False
        kwargs["trim_whitespace"] = False
        super().__init__(**kwargs)
        self.disable_validate_password = disable_validate_password

    def get_django_validators(self):
        """Return the list of Django password validators to be used."""
        raise NotImplementedError("Subclasses must implement this method.")

    def run_validators(self, value):
        """Run both DRF and Django password validators."""
        super().run_validators(value)

        if not self.disable_validate_password:
            self.validate_password(value)

    def validate_password(self, value):
        """Perform Django password validation."""
        try:
            user = self.context.get("user")
            validate_password(value, user=user, password_validators=self.get_django_validators())
        except DjangoValidationError as exc:
            raise ValidationError(get_error_detail(exc))


class PasswordSerializerField(BasePasswordField):
    """Password field with configurable Django validators."""

    def get_django_validators(self):
        """Return a specific set of Django password validators."""
        validator_config = [
            {
                "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {"min_length": self.MIN_LENGTH},
            },
            {
                "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
            },
        ]
        return get_password_validators(validator_config)


class EmailSerializerField(rest_framework.fields.EmailField):
    """Email field with configurable case sensitivity."""

    def __init__(self, **kwargs):
        kwargs["max_length"] = 256
        self.to_lower = kwargs.pop("to_lower", True)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        """Convert email to lowercase if required."""
        value = super().to_internal_value(data)
        return value.lower() if self.to_lower else value
