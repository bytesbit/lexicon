from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as dj_filters
from rest_framework import filters, serializers

from lexicon.api.pagination import DefaultPageNumberPagination, PaginatedListAPIViewMixin
from lexicon.api.views import GenericAPIView
from lexicon.video.models import Subtitle, Video


class SubtitleView(GenericAPIView):
    """
    API view to retrieve and cache subtitles for a given video file.
    """

    class Filterset(dj_filters.FilterSet):
        class Meta:
            model = Subtitle
            fields = ["language"]

    filter_backends = [dj_filters.DjangoFilterBackend]
    filterset_class = Filterset

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)

    def get(self, request, file_name, *args, **kwargs):
        """
        Retrieve subtitles for a given video file and cache the result.
        Only the first 1000 subtitles are processed for performance reasons.
        """
        start_time = request.query_params.get("start_time")

        if start_time:
            try:
                start_time = self.convert_to_time(start_time)
            except ValueError:
                return self.error_response(
                    message="Invalid start_time format. Expected format: HH:MM:SS,ms"
                )

        cache_key = f"subtitles_{file_name}_{start_time}"
        cached_subtitles = cache.get(cache_key)

        if cached_subtitles:
            return self.success_response(data={"subtitles": cached_subtitles})

        video = get_object_or_404(Video, video_file__icontains=file_name)

        subtitles = Subtitle.objects.filter(video=video)
        if start_time:
            subtitles = subtitles.filter(start_time__gte=start_time)

        subtitles = subtitles.order_by("start_time")
        filtered_subtitles = self.filter_queryset(subtitles)

        subtitle_list = [
            {
                "start_time": self.format_time(subtitle.start_time),
                "end_time": self.format_time(subtitle.end_time),
                "content": subtitle.cc_subtitle,
            }
            for subtitle in filtered_subtitles
        ]

        # Cache the result for 15 minutes
        cache.set(cache_key, subtitle_list, timeout=60 * 15)

        return self.success_response(data={"subtitles": subtitle_list})

    @staticmethod
    def format_time(time_obj):
        """
        Format time to 'HH:MM:SS,ms'.
        Example: '00:00:01,000'
        """
        return f"{time_obj.hour:02}:{time_obj.minute:02}:{time_obj.second:02},{time_obj.microsecond // 1000:03}"

    @staticmethod
    def convert_to_time(time_str):
        """
        Convert a string time in 'HH:MM:SS.microsecond' format to a time object.
        Example: '00:00:01.773000' -> time object
        """
        from datetime import time

        try:
            hours, minutes, seconds_microseconds = time_str.split(":")
            seconds, microseconds = map(int, seconds_microseconds.split("."))
            hours, minutes = int(hours), int(minutes)
            return time(hour=hours, minute=minutes, second=seconds, microsecond=microseconds)
        except (ValueError, IndexError):
            raise ValueError("Invalid time format")


class SubtitleVideoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to retrieve video details with custom video file name.
    """

    video_file_name = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "video_file_name",
        )

    def get_video_file_name(self, obj):
        """
        Extract and return the video file name without the full path.
        """
        return obj.video_file.name.split("/")[-1]


class SubtitleSearchView(PaginatedListAPIViewMixin, GenericAPIView):
    """
    API view to search for subtitles with pagination and case-sensitive search.
    """

    class OutPutSerializer(serializers.ModelSerializer):
        video = SubtitleVideoDetailSerializer()

        class Meta:
            model = Subtitle
            fields = (
                "id",
                "video",
                "cc_subtitle",
                "start_time",
            )

    class ListPagination(DefaultPageNumberPagination):
        pass

    queryset = Subtitle.objects.all()
    serializer_class = OutPutSerializer
    pagination_class = ListPagination
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["cc_subtitle"]

    def get_queryset(self):
        """
        Override the queryset to apply case-sensitive substring search.
        """
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(cc_subtitle__regex=rf"{search_query}")
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Return a paginated list of subtitles based on the search query.
        """
        return self.list(request, *args, **kwargs)
