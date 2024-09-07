import os

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lexicon.video.models import Video


class VideoPlaybackView(APIView):
    """
    API view for streaming video files.
    """

    def get(self, request, file_name, *args, **kwargs):
        video = get_object_or_404(Video, video_file__icontains=file_name)
        file_path = video.video_file.path

        if not os.path.exists(file_path):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        response = StreamingHttpResponse(self.get_video_stream(file_path), content_type="video/mp4")
        response["Content-Disposition"] = f'inline; filename="{file_name}"'
        return response

    def get_video_stream(self, file_path):
        """
        Generator function to stream the video file in chunks.
        """
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
