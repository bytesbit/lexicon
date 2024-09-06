import logging

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.permissions import AllowAny

from lexicon.api.fields import EmailSerializerField, PasswordSerializerField
from lexicon.auth.exceptions import InvalidCredentials
from lexicon.auth.views.signin_base import BaseUserSigninView

logger = logging.getLogger(__name__)


class UserEmailSigninAPI(BaseUserSigninView):
    """
    API view for user email-based sign-in.
    """

    LOGIN_METHOD = "email"

    class InputSerializer(serializers.Serializer):
        email = EmailSerializerField(required=True)
        password = PasswordSerializerField(required=True)

    serializer_class = InputSerializer
    permission_classes = [AllowAny]

    def authenticate_user(self, request, serializer):
        """
        Authenticate the user using email and password, and process the login.
        """
        data = serializer.validated_data
        email = data["email"]
        raw_password = data["password"]

        user = authenticate(request, username=email, password=raw_password)
        if not user:
            logger.info(f"Failed email login attempt for email: {email}.")
            raise InvalidCredentials(detail="Invalid email or password")

        logger.info(f"Successful email login for user [user_id={user.id}] with email: {email}.")

        return user
