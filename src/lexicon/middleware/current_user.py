import threading

from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def set_current_user(user):
    _thread_locals.user = user


def get_current_user():
    return getattr(_thread_locals, "user", None)


class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        set_current_user(getattr(request, "user", None))
