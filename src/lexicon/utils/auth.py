from typing import List
from urllib.parse import urlparse

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

INVALID_REDIRECT_URL_MSG = _("Invalid redirect URL. It does not match any allowed URLs.")


class URLValidator:
    """
    A utility class to handle URL validation against a list of allowed URLs.
    """

    @staticmethod
    def is_url_allowed(url: str, allowed_urls: List[str], check_path: bool = True) -> bool:
        """
        Checks if the given URL matches any of the allowed URLs.

        Args:
            url (str): The URL to validate.
            allowed_urls (List[str]): A list of allowed URLs.
            check_path (bool): Whether to check the path component of the URLs.

        Returns:
            bool: True if the URL is allowed, False otherwise.
        """
        parsed_url = urlparse(url)
        for allowed_url in allowed_urls:
            parsed_allowed_url = urlparse(allowed_url)
            if (
                parsed_url.scheme == parsed_allowed_url.scheme
                and parsed_url.netloc == parsed_allowed_url.netloc
            ):
                if check_path and parsed_url.path != parsed_allowed_url.path:
                    continue
                return True
        return False

    @staticmethod
    def validate_redirect_url(url: str, allowed_urls: List[str], check_path: bool = True):
        """
        Validates the given URL against the allowed URLs and raises an error if not valid.

        Args:
            url (str): The URL to validate.
            allowed_urls (List[str]): A list of allowed URLs.
            check_path (bool): Whether to check the path component of the URLs.

        Raises:
            serializers.ValidationError: If the URL is not allowed.
        """
        if not URLValidator.is_url_allowed(url, allowed_urls, check_path):
            raise serializers.ValidationError(INVALID_REDIRECT_URL_MSG)


def validate_login_redirect_url(url: str, check_path: bool = True):
    """
    Validates the login redirect URL against allowed login URLs in settings.

    Args:
        url (str): The URL to validate.
        check_path (bool): Whether to check the path component of the URLs.
    """
    URLValidator.validate_redirect_url(
        url, settings.ALLOWED_SSO_LOGIN_REDIRECT_TO_URLS, check_path=check_path
    )


def validate_logout_redirect_url(url: str, check_path: bool = True):
    """
    Validates the logout redirect URL against allowed logout URLs in settings.

    Args:
        url (str): The URL to validate.
        check_path (bool): Whether to check the path component of the URLs.
    """
    URLValidator.validate_redirect_url(
        url, settings.ALLOWED_SSO_LOGOUT_REDIRECT_TO_URLS, check_path=check_path
    )
