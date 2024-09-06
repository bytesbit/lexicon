import pathlib
from dataclasses import dataclass

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import DjangoValidationError

from lexicon.utils import bytes_to_mb


@dataclass
class UploadedFileConfig:
    # 'image', 'file', 'video', or 'audio'
    file_type: str

    def get_allowed_extensions(self):
        if self.file_type == "image":
            return ["png", "jpg", "jpeg"]
        if self.file_type == "file":
            return ["png", "jpeg", "jpg", "pdf", "doc", "docx", "xlsx"]
        if self.file_type == "video":
            return ["mp4", "avi", "mov", "webm"]
        if self.file_type == "audio":
            return ["mp3", "wav"]

    def get_allowed_max_size(self):
        if self.file_type == "image":
            return settings.IMAGE_FILE_UPLOAD_MAX_SIZE
        if self.file_type == "file":
            return settings.FILE_UPLOAD_MAX_SIZE
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


def validate_file(data, valid_file_types, max_file_size):
    file_name = data.name
    file_size = data.size
    file_ext = pathlib.PurePosixPath(file_name).suffix.strip(".").lower()
    valid_file_types = valid_file_types
    if file_ext not in valid_file_types:
        raise InvalidFileType(_(f"Unsupported file format, only support {valid_file_types}"))
    max_file_size = max_file_size
    if file_size > max_file_size:
        raise FileSizeLimitExceeded(
            _(
                "File size limit exceeded, should be less than %0.1f MB"
                % (bytes_to_mb(max_file_size))
            )
        )
    return data


def validate_image_file(data):
    return validate_file(
        data,
        valid_file_types=["png", "jpg", "jpeg"],
        max_file_size=settings.IMAGE_FILE_UPLOAD_MAX_SIZE,
    )


def validate_video_file(data):
    return validate_file(
        data,
        valid_file_types=["mp4", "avi", "mov", "webm"],
        max_file_size=settings.VIDEO_FILE_UPLOAD_MAX_SIZE,
    )


def validate_audio_file(data):
    return validate_file(
        data,
        valid_file_types=["mp3", "wav"],
        max_file_size=settings.AUDIO_FILE_UPLOAD_MAX_SIZE,
    )
