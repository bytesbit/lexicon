from django.urls import path

from lexicon.video.views.playback import VideoPlaybackView
from lexicon.video.views.video import UploadAndListView, VideoListCreateView

urlpatterns = [
    path("list/", UploadAndListView.as_view(), name="video-list"),
    path("api/v1/videos/", VideoListCreateView.as_view(), name="video-upload"),
    path(
        "api/v1/video/playback/<str:file_name>/", VideoPlaybackView.as_view(), name="video-playback"
    ),
]
