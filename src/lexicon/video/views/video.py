import logging

from django.shortcuts import render
from rest_framework import filters, serializers, status
from rest_framework.exceptions import ValidationError

from lexicon.api.file_upload import UploadedFileConfig
from lexicon.api.pagination import DefaultPageNumberPagination, PaginatedListAPIViewMixin
from lexicon.api.views import GenericAPIView
from lexicon.video.models import Video
from lexicon.video.services.video import create_video_entity

logger = logging.getLogger(__name__)


class UploadAndListView(GenericAPIView):
    """
    View for rendering the video upload and list page.
    """

    template_name = "video/list.html"
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to render the video upload and listing page.
        """
        return render(request, self.template_name)


class VideoListCreateView(
    PaginatedListAPIViewMixin,
    GenericAPIView,
):
    """
    API view for listing and uploading videos.
    """

    permission_classes = []

    class ListPagination(DefaultPageNumberPagination):
        pass

    class VideoInputSerializer(serializers.Serializer):
        """
        Serializer for video input, handling file validation and metadata.
        """

        title = serializers.CharField(max_length=255)
        description = serializers.CharField(max_length=200, required=False)
        video_file = serializers.FileField()

        def validate(self, attrs):
            file_config = UploadedFileConfig(file_type="video")
            field = file_config.get_serializer_field()
            field.run_validation(attrs["video_file"])
            return attrs

    class VideoOutputSerializer(serializers.ModelSerializer):
        """
        Serializer for video output, handling the display of video information.
        """

        file_name = serializers.SerializerMethodField()

        class Meta:
            model = Video
            fields = ["id", "title", "description", "file_name", "created_at"]

        def get_file_name(self, obj):
            return obj.video_file.name.split("/")[1]

    pagination_class = ListPagination
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoOutputSerializer
    filter_backends = [
        filters.SearchFilter,
    ]

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve the list of videos.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to upload a new video.
        """
        serializer = self.VideoInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            create_video_entity(
                title=data["title"],
                description=data.get("description"),
                video_file=data["video_file"],
            )
            logger.info(f"Video '{data['title']}' uploaded successfully.")
            return self.success_response(
                {"message": "File uploaded successfully"}, status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            logger.error(f"Validation error while uploading video: {e}")
            return self.success_response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error while uploading video: {e}")
            return self.success_response(
                {"message": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
