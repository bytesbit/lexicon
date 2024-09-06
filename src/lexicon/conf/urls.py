"""lexicon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from lexicon._version import VERSION

admin.site.site_title = _(settings.BACKEND_ADMIN_SITE_TITLE)
admin.site.site_header = _(f"{settings.BACKEND_ADMIN_SITE_HEADER} - {VERSION}")
admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("lexicon.auth.urls", "lexicon.auth"), namespace="lexicon_auth")),
]
