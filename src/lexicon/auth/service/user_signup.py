import logging

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from lexicon.auth.exceptions import UserAlreadyExists
from lexicon.models import User

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def create_user(
        first_name: str,
        email: str,
        password: str,
        last_name: str = None,
        send_welcome_email: bool = True,
    ) -> User:
        """
        Creates a new user with the provided details, and returns the user object.

        Args:
            first_name (str): User's first name.
            email (str): User's email address.
            password (str): User's password.
            last_name (str, optional): User's last name. Defaults to None.
            send_welcome_email (bool): Flag to trigger welcome email. Defaults to True.

        Returns:
            User: The newly created User instance.

        Raises:
            UserAlreadyExists: If the user with the given email already exists.
            ValueError: If validation fails (e.g., bad input).
        """
        logger.debug("Initiating user signup process for email: %s", email)

        email = UserService.normalize_email(email)

        UserService._validate_unique_email(email)

        # Transaction block to ensure atomicity of user creation
        try:
            with transaction.atomic():
                # Create and save user
                logger.debug("Creating user instance for email: %s", email)
                user = UserService._create_user_instance(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )

                # Optional: Send welcome email
                if send_welcome_email:
                    UserService._send_welcome_email(user)

                logger.info("User '%s' created successfully.", user.email)
                return user

        except Exception as e:
            logger.exception("Error while creating user '%s': %s", email, e)
            raise

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize the email address by lowercasing and stripping whitespace."""
        return User.normalize_email(email.strip().lower())

    @staticmethod
    def _validate_unique_email(email: str):
        """Validate that the email is unique."""
        if User.objects.filter(email=email).exists():
            logger.error("User creation failed: Email '%s' already exists.", email)
            raise UserAlreadyExists(_("Please use a different email or contact admin."))

    @staticmethod
    def _create_user_instance(first_name: str, last_name: str, email: str, password: str) -> User:
        """Create the User instance and save it to the database."""
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
        )
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def _send_welcome_email(user: User):
        """Send a welcome email to the user."""
        # Placeholder for sending a welcome email to the new user
        # Extend this method as needed to integrate email services
        logger.debug("Sending welcome email to user '%s'.", user.email)
        # Implement email-sending logic here.
