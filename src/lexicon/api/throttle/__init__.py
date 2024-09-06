import functools
import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle

logger = logging.getLogger(__name__)

__all__ = [
    "AnonRateThrottle",
    "ResponseStatusCodeThrottle",
    "SimpleRateThrottle",
]


class ConcurrencyThrottledError(exceptions.APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _("You have reached a concurrency limit. Please try again after " "some time")
    default_code = "throttled"


class BurstAnonRateThrottle(AnonRateThrottle):
    scope = "anon_burst"


class ResponseStatusCodeThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by an anonymous or an
    authenticated user based on the response status code. Throttling is applied
    to any view that has the `throttle_scope` property or has passed the value
    of `scope` as a kwarg while initializing this class.

    Throttling can be used in two ways:

    1. Use it as a decorator on the view method:
       ```python
       class MyView(ApiView):
           @ResponseStatusCodeThrottle(status_codes=[400],throttle_scope='scope_name')
           def post(request, *args, **kwargs):
               pass
       ```

    2. Add this class to the `throttle_classes` attribute in the view class and
       explicitly call `ResponseStatusCodeThrottle.throttle_status_code()`
       within the view:
       ```python
       class MyView(ApiView):
           throttle_classes = [ResponseStatusCodeThrottle,]
           throttle_scope = ''
           def post(request, *args, **kwargs):
               throttle = ResponseStatusCodeThrottle(status_codes=[400])
               # Do whatever you want to do
               # Before returning the response, call
               throttle.throttle_status_code(request, self,
                                             status_code=response.status_code)
               pass
       ```
    """

    scope_attr = "throttle_scope"

    def __init__(self, status_codes=None, throttle_scope=None):
        """
        Initializes the throttle class with the provided status codes and scope.
        """
        self.status_codes = status_codes or []
        self.scope = throttle_scope

    def __call__(self, view_method, *args, **kwargs):
        """
        Decorator that applies the throttling logic to the wrapped view method.
        """
        throttle = self

        @functools.wraps(view_method)
        def wrapper(view, request, *args, **kwargs):
            # Perform throttling check
            if not throttle.allow_request(request, view):
                duration = max([throttle.wait()], default=None)
                view.throttled(request, duration)

            response = view_method(view, request, *args, **kwargs)

            if isinstance(response, Response):
                throttle.throttle_status_code(request, view, status_code=response.status_code)
            return response

        return wrapper

    def _throttle_success(self, request, view):
        """
        Overrides the base class method to update the throttling history based on
        the response status code.
        """
        if self._allow_request(view):
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Drop any requests from the history that have now passed the throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()

        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
        return True

    def throttle_success(self):
        """
        Overrides the base class method to always return True, as the success
        of throttling is determined based on the response status code.
        """
        return True

    def _allow_request(self, view):
        """
        Determines if the request is allowed based on the throttle scope.
        Initializes the values of `rate`, `num_requests`, and `duration`.
        """
        self.scope = getattr(self, "scope", None) or getattr(view, self.scope_attr, None)
        if not self.scope:
            return True

        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return False

    def allow_request(self, request, view):
        """
        Determines if the request is allowed based on the throttle scope.
        Calls `_allow_request` method to initialize the throttle values.
        """
        if self._allow_request(view):
            return True
        return super().allow_request(request, view)

    def throttle_status_code(self, request, view, status_code=None):
        """
        Call this method before sending the response in the view to apply throttling
        based on the response status code.
        """
        if status_code in self.status_codes:
            self._throttle_success(request, view)

    def get_cache_key(self, request, view):
        """
        Generates a unique cache key by concatenating the user ID with the
        `throttle_scope` property of the view, if set.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}
