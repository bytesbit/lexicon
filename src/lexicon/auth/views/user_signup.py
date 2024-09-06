import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny

from lexicon.api.fields import EmailSerializerField, PasswordSerializerField
from lexicon.api.throttle import ResponseStatusCodeThrottle
from lexicon.api.views import GenericAPIView
from lexicon.auth.exceptions import UserAlreadyExists
from lexicon.auth.service.user_signup import UserService
from lexicon.models import User

logger = logging.getLogger(__name__)


class UserSignupAPI(GenericAPIView):
    """
    API view to handle user signup requests.
    """

    class InputSerializer(serializers.Serializer):
        """
        Serializer for validating user signup input.
        """

        first_name = serializers.CharField(max_length=100)
        last_name = serializers.CharField(max_length=100, required=False)
        email = EmailSerializerField(required=True)
        password = PasswordSerializerField(required=True)

        def validate(self, attrs):
            """
            Validate the input data. Check if the user already exists.
            """
            if User.objects.filter(email=attrs.get("email")).exists():
                raise UserAlreadyExists(_("A user with this email already exists."))
            return attrs

    serializer_class = InputSerializer
    permission_classes = [AllowAny]

    @ResponseStatusCodeThrottle(
        status_codes=[status.HTTP_400_BAD_REQUEST],
        throttle_scope="user_signup_fail",
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user signup.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            user = UserService.create_user(
                first_name=validated_data.data["first_name"],
                email=validated_data["email"],
                password=validated_data["password"],
                last_name=validated_data.get("last_name"),
            )
            logger.info(f"User created successfully: {user}")
            return self.success_response(
                data={"message": _("Account successfully created.")},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return self.success_response(
                data={"message": _("User creation failed. Please try again.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
