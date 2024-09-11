import logging
import os
import re
import subprocess

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from lexicon.tasks.base import instrumented_task

from .models import Subtitle, Video

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, video_id, language="eng"):
        self.video_id = video_id
        self.video = self._get_video_cached(video_id)
        self.video_path = self.video.video_file.path if self.video else ""
        self.subtitle_path = ""
        self.language = language

    @staticmethod
    def _get_video_cached(video_id):
        """
        Fetch the video object with caching to avoid repeated DB lookups.
        """
        cache_key = f"video_{video_id}"
        video = cache.get(cache_key)
        if not video:
            try:
                video = Video.objects.get(id=video_id)
                cache.set(cache_key, video, timeout=3600)
            except ObjectDoesNotExist:
                raise ValueError("Video not found")
        return video

    def extract_subtitles(self):
        """
        Extract subtitles from a video file asynchronously using subprocess.
        """
        if not self.video:
            raise ValueError("Video object is not initialized.")

        input_path = os.path.join(settings.MEDIA_ROOT, self.video.video_file.name)
        output_filename = f"{os.path.splitext(self.video.video_file.name)[0]}_{self.language}.srt"
        output_path = os.path.join(settings.MEDIA_ROOT, "subtitles", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        stream_mapping = {
            "eng": 2,
            "kor": 4,
            "ger": 5,
        }
        stream = stream_mapping.get(self.language, 2)

        command = ["ffmpeg", "-i", input_path, "-map", f"0:{stream}", "-c:s", "copy", output_path]

        try:
            subprocess.run(command, check=True, stderr=subprocess.PIPE, text=True)
            self.subtitle_path = output_path
            logger.info(f"Subtitles extracted to: {output_path}")
        except Exception as e:
            logger.exception(f"Failed to extract subtitles: {e}")
            raise

    def read_subtitle_file(self):
        """
        Asynchronously read and parse the subtitle file.
        """
        subtitle_entries = []
        try:
            with open(self.subtitle_path, "r", encoding="utf-8") as file:
                content = file.read()

            subtitle_pattern = r"(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.+?)\s*(?=\n\d|\Z)"
            matches = re.findall(subtitle_pattern, content, re.DOTALL)

            for match in matches:
                entry = {
                    "start_time": self._convert_srt_time(match[1]),
                    "end_time": self._convert_srt_time(match[2]),
                    "cc_subtitle": match[3].replace("\n", " ").strip(),
                }
                subtitle_entries.append(entry)
        except FileNotFoundError:
            logger.error(f"Subtitle file {self.subtitle_path} not found.")
            raise
        except Exception as e:
            logger.error(f"Error reading subtitle file: {e}")
            raise

        return subtitle_entries

    @staticmethod
    def _convert_srt_time(srt_time_str):
        """
        Convert SRT timestamp to Python `time` object (HH:MM:SS,MS).
        """
        from datetime import datetime

        time_format = "%H:%M:%S,%f"
        return datetime.strptime(srt_time_str, time_format).time()

    @transaction.atomic
    def save_subtitle_to_db(self, subtitle_entries):
        """
        Save the parsed subtitle entries to the database using bulk_create for efficiency.
        """
        subtitles_to_create = [
            Subtitle(
                video=self.video,
                language=self.language,
                cc_subtitle=entry["cc_subtitle"],
                start_time=entry["start_time"],
                end_time=entry["end_time"],
            )
            for entry in subtitle_entries
        ]

        Subtitle.objects.bulk_create(subtitles_to_create)
        logger.info(
            f"{len(subtitles_to_create)} subtitles saved to the database for video {self.video_id}."
        )

    def clean_up(self):
        """
        Remove the temporary subtitle file if it exists.
        """
        if os.path.exists(self.subtitle_path):
            os.remove(self.subtitle_path)
            logger.info(f"Removed temporary subtitle file {self.subtitle_path}")

    def process(self):
        """
        Process the video asynchronously, extract subtitles, and save them to the database.
        """
        try:
            self.extract_subtitles()
            subtitle_entries = self.read_subtitle_file()
            self.save_subtitle_to_db(subtitle_entries)
        except Exception as e:
            logger.error(f"Error processing video {self.video_id}: {e}")
        finally:
            ...
            # self.clean_up()


@instrumented_task(name="lexicon.video.extraction.process_video")
def process_video(video_id, language=None):
    """
    Celery task to process a video asynchronously.
    """
    processor = VideoProcessor(video_id, language=language)
    processor.process()
