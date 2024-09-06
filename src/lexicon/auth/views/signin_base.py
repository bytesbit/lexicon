import logging

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from lexicon.api.throttle import ResponseStatusCodeThrottle
from lexicon.api.views import GenericAPIView
from lexicon.auth.exceptions import AuthenticationFailed, UserEmailNotVerified
from lexicon.models import User

logger = logging.getLogger(__name__)


class BaseUserSigninView(GenericAPIView):
    """
    Base class for handling user sign-in. Must be extended to provide
    a specific authentication method.
    """

    LOGIN_METHOD = None  # Either 'email' or 'mobile', must be set in subclasses

    def authenticate_user(self, request, serializer) -> User:
        """
        Abstract method for user authentication.
        Subclasses must implement this method to return an authenticated user.

        Args:
            request: The HTTP request object.
            serializer: The validated serializer data.

        Returns:
            User: The authenticated user instance.

        Raises:
            NotImplementedError: If the method is not overridden in subclasses.
        """
        raise NotImplementedError(".authenticate_user() must be overridden in subclass.")

    def get_user_by_email(self, email: str) -> User:
        """
        Retrieves a user by email, case-insensitively.

        Args:
            email (str): The email to search for.

        Returns:
            User or None: The user instance if found, or None if not found.
        """
        return User.objects.filter(email__iexact=email).first()

    def login_user(self, request, user: User) -> RefreshToken:
        """
        Logs in a user, verifies their email (if applicable), and generates tokens.

        Args:
            request: The HTTP request object.
            user: The user instance to log in.

        Returns:
            RefreshToken: The refresh token generated for the user.

        Raises:
            UserEmailNotVerified: If the user's email is not verified.
        """
        if self.LOGIN_METHOD == "email" and not user.email_verified:
            logger.warning(f"Email not verified for user: {user.email}")
            raise UserEmailNotVerified()

        # Generate refresh token
        refresh = RefreshToken.for_user(user)

        # Update the last login time
        self.update_last_login(user)

        return refresh

    @staticmethod
    def update_last_login(user: User):
        """
        Updates the last login timestamp for a user.

        Args:
            user: The user instance to update.
        """
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        logger.info(f"Updated last login for user: {user.id}")

    def prepare_login_response(self, refresh: RefreshToken) -> dict:
        """
        Prepares the successful login response with tokens and expiration times.

        Args:
            refresh: The refresh token generated for the user.

        Returns:
            dict: The response data with tokens and their expiration times.
        """
        access_token = refresh.access_token
        return {
            "refresh_token": str(refresh),
            "refresh_exp_at": refresh["exp"],
            "access_token": str(access_token),
            "access_exp_at": access_token["exp"],
        }

    def do_login_and_prepare_response(self, request, user: User):
        """
        Handles user login and prepares the final response.

        Args:
            request: The HTTP request object.
            user: The authenticated user instance.

        Returns:
            Response: A success response containing token data.
        """
        logger.info(f"Logging in user: {user.id}")
        refresh = self.login_user(request, user)
        response_data = self.prepare_login_response(refresh)
        return self.success_response(
            status=status.HTTP_200_OK,
            data=response_data,
        )

    @ResponseStatusCodeThrottle(
        status_codes=[status.HTTP_400_BAD_REQUEST], throttle_scope="login_bad_attempt"
    )
    def post(self, request, *args, **kwargs):
        """
        Handles user sign-in requests. Validates input and performs authentication.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A response containing tokens if successful, or error messages.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.authenticate_user(request, serializer)
        if user is None:
            logger.error("Authentication failed: No user returned.")
            raise AuthenticationFailed(detail=_("Authentication failed."))

        return self.do_login_and_prepare_response(request, user)
