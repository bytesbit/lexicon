from dataclasses import dataclass
from typing import List, Optional, Union

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import DjangoValidationError


@dataclass
class UploadedFileConfig:
    """
    Configuration for file uploads including allowed file types, extensions, and size limits.

    Attributes:
        file_type (str): The type of the file being uploaded ('video', 'audio', etc.).
    """

    file_type: str

    def get_allowed_extensions(self) -> List[str]:
        """
        Returns a list of allowed file extensions based on the file type.

        Returns:
            List[str]: List of allowed file extensions.
        """
        if self.file_type == "video":
            return ["webm"]
        if self.file_type == "audio":
            return ["mp3", "wav"]
        return []

    def get_allowed_max_size(self) -> int:
        """
        Returns the maximum allowed file size based on the file type.

        Returns:
            int: Maximum allowed file size in bytes.
        """
        if self.file_type == "video":
            return settings.VIDEO_FILE_UPLOAD_MAX_SIZE
        return settings.FILE_UPLOAD_MAX_SIZE

    def get_serializer_field(self) -> serializers.Field:
        """
        Returns a DRF serializer field with validators based on the file type.

        Returns:
            serializers.Field: Configured serializer field for the file type.
        """
        allowed_max_size = self.get_allowed_max_size()
        allowed_extensions = self.get_allowed_extensions()

        return serializers.FileField(
            validators=[
                FileSizeValidator(allowed_max_size=allowed_max_size),
                FileExtensionValidator(allowed_extensions=allowed_extensions),
            ]
        )


@deconstructible
class FileSizeValidator:
    """
    Validator for checking file size limits.

    Attributes:
        message (str): Error message to be used if the file size exceeds the limit.
        code (str): Error code to be used if the file size exceeds the limit.
        allowed_max_size (int): Maximum allowed file size in bytes.
    """

    message = _("File size is too large. Allowed max file size: %(allowed_max_size)s bytes.")
    code = "file_too_large"

    def __init__(
        self,
        allowed_max_size: Optional[int] = None,
        message: Optional[str] = None,
        code: Optional[str] = None,
    ):
        """
        Initializes the validator with the specified maximum size, message, and code.

        Args:
            allowed_max_size (Optional[int]): The maximum allowed file size in bytes.
            message (Optional[str]): Custom error message.
            code (Optional[str]): Custom error code.
        """
        self.allowed_max_size = allowed_max_size or settings.FILE_UPLOAD_MAX_SIZE
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value: Union[None, serializers.FileField]):
        """
        Validates the size of the file. Raises a validation error if the file size exceeds the allowed limit.

        Args:
            value (Union[None, serializers.FileField]): The file to be validated.

        Raises:
            DjangoValidationError: If the file size exceeds the allowed limit.
        """
        file_size = value.size
        if file_size > self.allowed_max_size:
            raise DjangoValidationError(
                self.message,
                code=self.code,
                params={"allowed_max_size": self.allowed_max_size},
            )
