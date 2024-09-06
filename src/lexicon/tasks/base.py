import logging
from functools import wraps
from typing import Union

from celery import shared_task
from celery._state import get_current_task
from sentry_sdk import configure_scope

from lexicon.celery import app
from lexicon.models import User

__all__ = (
    "instrumented_task",
    "shared_task",
)

logger = logging.getLogger(__name__)


def get_task_actor(actor) -> Union[User, None]:
    if isinstance(actor, User):
        return actor
    pk_value = User._meta.pk.to_python(actor)
    try:
        return User.objects.get(pk=pk_value)
    except User.DoesNotExist:
        return None


def instrumented_task(name, **task_kwargs):
    # set serializer to pickle for below actor support
    task_kwargs.setdefault("serializer", "pickle")

    def wrapped(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            task = get_current_task()
            logger.debug(f"running task : {task.name}[{task.request.id}]")
            # if actor is passed by task caller then actor details
            # will be logged in sentry event's context (if
            # raised any), for tracking the owner of celery task
            actor = get_task_actor(kwargs.pop("actor", None))
            if actor:
                logger.debug(f"setting actor in task kwargs and sentry : {actor}")
                kwargs["actor"] = actor
                with configure_scope() as scope:
                    scope.set_user(
                        {
                            "id": actor.id,
                            "email": actor.email,
                            "username": actor.username,
                        }
                    )

            result = func(*args, **kwargs)
            logger.debug(f"task completed : {task.name}[{task.request.id}]")
            return result

        return app.task(name=name, **task_kwargs)(_wrapped)

    return wrapped
