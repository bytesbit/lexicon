import logging
from functools import wraps

from celery import shared_task
from celery._state import get_current_task

from lexicon.celery import app

__all__ = (
    "instrumented_task",
    "shared_task",
)

logger = logging.getLogger(__name__)


def instrumented_task(name: str, **task_kwargs):
    """
    A decorator for creating instrumented Celery tasks with actor tracking and logging.

    This decorator wraps the task function, logs task execution, and tracks the actor
    (if provided) for better monitoring and debugging, including sentry integration.

    Args:
        name (str): The name of the Celery task.
        **task_kwargs: Additional arguments to pass to the Celery task.

    Returns:
        function: The wrapped task function.
    """
    task_kwargs.setdefault("serializer", "pickle")

    def wrapped(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            task = get_current_task()
            logger.debug(f"Running task: {task.name}[{task.request.id}]")
            result = func(*args, **kwargs)
            logger.debug(f"Task completed: {task.name}[{task.request.id}]")
            return result

        return app.task(name=name, **task_kwargs)(_wrapped)

    return wrapped
