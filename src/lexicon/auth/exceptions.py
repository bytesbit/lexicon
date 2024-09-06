from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ValidationError


class UserAlreadyExists(ValidationError):
    default_detail = _("User with email address already exists")
    default_code = "user_exists"

    def __init__(self, attempts_left=None, **kwargs):
        detail = kwargs.pop("detail", self.default_detail)
        super().__init__(detail, **kwargs)


class InvalidCredentials(ValidationError):
    default_detail = _("Invalid credentials")
    default_code = "invalid_credentials"

    def __init__(self, attempts_left=None, **kwargs):
        detail = kwargs.pop("detail", self.default_detail)
        super().__init__(detail, **kwargs)


class UserEmailNotVerified(AuthenticationFailed):
    pass
