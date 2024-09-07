from dataclasses import dataclass

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import DjangoValidationError


@dataclass
class UploadedFileConfig:
    file_type: str

    def get_allowed_extensions(self):
        if self.file_type == "video":
            return ["mp4", "avi", "mov", "webm"]
        if self.file_type == "audio":
            return ["mp3", "wav"]

    def get_allowed_max_size(self):
        if self.file_type == "video":
            return settings.VIDEO_FILE_UPLOAD_MAX_SIZE
        if self.file_type == "audio":
            return settings.AUDIO_FILE_UPLOAD_MAX_SIZE

    def get_serializer_field(self):
        allowed_max_size = self.get_allowed_max_size()
        allowed_extensions = self.get_allowed_extensions()
        if self.file_type == "image":
            return serializers.ImageField(
                validators=[
                    FileSizeValidator(allowed_max_size=allowed_max_size),
                    FileExtensionValidator(allowed_extensions=allowed_extensions),
                ]
            )

        return serializers.FileField(
            validators=[
                FileSizeValidator(allowed_max_size=allowed_max_size),
                FileExtensionValidator(allowed_extensions=allowed_extensions),
            ]
        )


class InvalidFileType(serializers.ValidationError):
    pass


class FileSizeLimitExceeded(serializers.ValidationError):
    pass


@deconstructible
class FileSizeValidator:
    message = _("File size is too large. Allowed max file size: " "%(allowed_max_size)s bytes.")
    code = "file_too_large"

    def __init__(self, allowed_max_size=None, message=None, code=None):
        if allowed_max_size is None:
            allowed_max_size = settings.FILE_UPLOAD_MAX_SIZE
        self.allowed_max_size = allowed_max_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        # `UploadedFile` objects should have size attribute.
        file_size = value.size
        if file_size > self.allowed_max_size:
            raise DjangoValidationError(
                self.message,
                code=self.code,
                params={"allowed_max_size": self.allowed_max_size},
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.allowed_extensions == other.allowed_extensions
            and self.message == other.message
            and self.code == other.code
        )
