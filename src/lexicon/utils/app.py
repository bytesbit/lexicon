import os

from configurations import importer


def setup_app_config():
    if not importer.installed:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lexicon.conf.settings")
        os.environ.setdefault("DJANGO_CONFIGURATION", "Development")
        import configurations

        configurations.setup()
