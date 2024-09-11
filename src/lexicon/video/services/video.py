import logging

from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from lexicon.video.extraction import process_video
from lexicon.video.models import Video

logger = logging.getLogger(__name__)


def create_video_entity(
    title: str, video_file: UploadedFile, description: str, language: str
) -> Video:
    """
    Creates a new video entity in the database with the given title, video file, and description.

    This function checks for the existence of a video with the same title and raises
    a ValidationError if it already exists. If not, it creates a new Video object and logs the process.

    Args:
        title (str): The title of the video.
        video_file (UploadedFile): The video file to be uploaded.
        description (str): A brief description of the video.
    """
    logger.debug("Attempting to create video with title: '%s'", title)

    if Video.objects.filter(title=title).exists():
        error_message = _("A video with the title '{}' already exists.".format(title))
        logger.error(error_message)
        raise serializers.ValidationError(error_message)

    video = Video.objects.create(title=title, description=description, video_file=video_file)

    logger.info("Video created successfully with title: '%s'", title)

    if language not in ["eng", "kor", "ger"]:
        raise serializers.ValidationError(_("Please select valid language"))

    process_video.delay(video.id, language)

    return video
