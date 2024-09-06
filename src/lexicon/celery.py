from celery import Celery, Task
from django.conf import settings

from lexicon.apps import setup_app_config
from lexicon.utils.celery import TransactionAwareTaskMixin

setup_app_config()


class BaseTask(TransactionAwareTaskMixin, Task):
    pass


app = Celery("lexicon", task_cls="lexicon.celery:BaseTask")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
