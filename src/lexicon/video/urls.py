from django.urls import path

from lexicon.video.views.playback import VideoPlaybackView
from lexicon.video.views.subtitle import SubtitleSearchView, SubtitleView
from lexicon.video.views.video import VideoListCreateView, VideoPageListView

urlpatterns = [
    path("list/", VideoPageListView.as_view(), name="video-list"),
    path("api/v1/videos/", VideoListCreateView.as_view(), name="video-upload"),
    path(
        "api/v1/video/playback/<str:file_name>/", VideoPlaybackView.as_view(), name="video-playback"
    ),
    path(
        "api/v1/videos/subtitle/<str:file_name>/",
        SubtitleView.as_view(),
        name="video-subtitle",
    ),
    path(
        "api/v1/videos/subtitles/",
        SubtitleSearchView.as_view(),
        name="video-subtitle-search",
    ),
]
