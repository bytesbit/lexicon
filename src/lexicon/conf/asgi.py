"""
ASGI config for lexicon project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lexicon.conf.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Development")

from configurations.asgi import get_asgi_application  # noqa: E402

application = get_asgi_application()
