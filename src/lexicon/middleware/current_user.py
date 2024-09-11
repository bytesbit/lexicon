import threading

from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def set_current_user(user):
    """
    Store the current user in a thread-local variable.

    Args:
        user (User): The user object to be stored.
    """
    _thread_locals.user = user


def get_current_user():
    """
    Retrieve the current user from the thread-local variable.

    Returns:
        User: The currently stored user object, or None if no user is set.
    """
    return getattr(_thread_locals, "user", None)


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Middleware that sets the current user for each request.

    This middleware retrieves the user from the request object and stores it
    in a thread-local variable, which can be accessed using `get_current_user()`.

    Methods:
        process_request(request):
            Sets the current user for the current request.
    """

    def process_request(self, request):
        """
        Process the incoming request and set the current user.

        Args:
            request (HttpRequest): The incoming request object containing the user.
        """
        set_current_user(getattr(request, "user", None))
