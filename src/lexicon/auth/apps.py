from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LexiconConfig(AppConfig):
    name = "lexicon.auth"
    label = "lexicon_auth"
    verbose_name = _("Lexicon Auth")

    def ready(self):
        pass
