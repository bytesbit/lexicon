import os

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lexicon.video.models import Video


class VideoPlaybackView(APIView):
    """
    API view for streaming video files with support for range requests.
    """

    def get(self, request, file_name, *args, **kwargs):
        """
        Handle GET requests to stream a video file. Supports range requests for partial content streaming.
        """
        video = self.get_video(file_name)
        if isinstance(video, Response):
            return video

        file_path = video.video_file.path
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get("Range")

        if range_header:
            return self.handle_range_request(range_header, file_path, file_size)
        else:
            return self.stream_full_video(file_path, file_name, file_size)

    def get_video(self, file_name):
        """
        Retrieve the video object based on the file name. Return a 404 response if not found.
        """
        video = get_object_or_404(Video, video_file__icontains=file_name)
        file_path = video.video_file.path

        if not os.path.exists(file_path):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        return video

    def handle_range_request(self, range_header, file_path, file_size):
        """
        Handle HTTP Range requests for partial video streaming.
        """
        try:
            start, end = self.parse_byte_range(range_header, file_size)
            if start >= file_size:
                return HttpResponse(status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

            end = min(end, file_size - 1)
            content_length = end - start + 1

            response = StreamingHttpResponse(
                self.get_video_stream(file_path, start, end + 1),
                status=status.HTTP_206_PARTIAL_CONTENT,
                content_type="video/mp4",
            )
            response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
            response["Content-Length"] = str(content_length)
            return response
        except ValueError:
            return HttpResponse(status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def parse_byte_range(self, range_header, file_size):
        """
        Parse the 'Range' header and return the start and end byte positions.
        """
        byte_range = range_header.strip().replace("bytes=", "")
        start, end = byte_range.split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
        return start, end

    def stream_full_video(self, file_path, file_name, file_size):
        """
        Stream the full video if no range request is provided.
        """
        response = StreamingHttpResponse(self.get_video_stream(file_path), content_type="video/mp4")
        response["Content-Disposition"] = f'inline; filename="{file_name}"'
        response["Content-Length"] = str(file_size)
        return response

    def get_video_stream(self, file_path, start=0, end=None):
        """
        Generator function to stream the video file in chunks.
        """
        chunk_size = self.get_chunk_size()
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = (end - start) if end else None

            while remaining is None or remaining > 0:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                if remaining is not None:
                    if len(chunk) > remaining:
                        chunk = chunk[:remaining]
                    remaining -= len(chunk)
                yield chunk

    @staticmethod
    def get_chunk_size():
        """
        Return the optimal chunk size for streaming the video.
        """
        return 8192  # Chunk size can be configured or optimized later based on testing
