import json
from functools import wraps
from typing import Callable, TypeVar, Union
from uuid import UUID

from django.core.cache import cache
from django.http import HttpRequest
from rest_framework.response import Response

ViewType = TypeVar("ViewType")


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle UUID serialization.
    """

    def default(self, obj):
        """
        Serializes objects as strings if they cannot be handled by the default encoder.
        """

        if isinstance(obj, UUID):
            return str(obj)
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def cache_view_response(key: Union[str, Callable[[HttpRequest, "ViewType"], str]], timeout: int):
    """
    Decorator to cache view responses with custom cache keys.

    Args:
        key (str or Callable[[HttpRequest, ViewType], str]): Base cache key or a function to generate the cache key.
        timeout (int): Cache expiration timeout in seconds.

    Returns:
        function: Decorated view function.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, request, *args, **kwargs):
            if isinstance(key, str):
                cache_key = key
            elif callable(key):
                cache_key = key(request, view)
            else:
                raise Exception("Unsupported key value")

            response_data = cache.get(cache_key)

            if not response_data:
                response = view_func(view, request, *args, **kwargs)
                response_data = response.data
                cache.set(cache_key, json.dumps(response_data, cls=CustomJSONEncoder), timeout)
            else:
                response_data = json.loads(response_data)

            return Response(response_data)

        return _wrapped_view

    return decorator


def cached_method_result(key: Union[str, Callable[[ViewType], str]], timeout: int):
    """
    Decorator to cache method results with custom cache keys.

    Args:
        key (str or Callable[[ViewType], str]): Base cache key or a function to generate the cache key.
        timeout (int): Cache expiration timeout in seconds.

    Returns:
        function: Decorated method.

    Example:
        Usage with a class method:

    ```python
        class MyClass:
            @cached_method_result("MY_CACHE_KEY", 60)
            def my_method(self, arg1, arg2):
                return result_data
    ```
    """

    def decorator(method):
        @wraps(method)
        def _wrapped_method(self, *args, **kwargs):
            if isinstance(key, str):
                cache_key = key
            elif callable(key):
                cache_key = key(self)
            else:
                raise Exception("Unsupported key value")

            result_data = cache.get(cache_key)

            if not result_data:
                result_data = method(self, *args, **kwargs)
                cache.set(cache_key, json.dumps(result_data, cls=CustomJSONEncoder), timeout)
            else:
                result_data = json.loads(result_data)

            return result_data

        return _wrapped_method

    return decorator


def cache_function_result(key: Union[str, Callable[[ViewType], str]], timeout: int):
    """
    Decorator to cache function results with custom cache keys.

    Args:
        key (str or Callable[[ViewType], str]): Base cache key or a function to generate the cache key.
        timeout (int): Cache expiration timeout in seconds.

    Returns:
        function: Decorated method.

    Example:
        Usage with a function:

    ```python
            @cached_function_result("MY_CACHE_KEY", 60)
            def my_function(arg1, arg2):
                return result_data
    ```
    """

    def decorator(method):
        @wraps(method)
        def _wrapped_method(*args, **kwargs):
            if isinstance(key, str):
                cache_key = key
            elif callable(key):
                cache_key = key(*args, **kwargs)
            else:
                raise Exception("Unsupported key value")

            result_data = cache.get(cache_key)

            if not result_data:
                result_data = method(*args, **kwargs)
                cache.set(cache_key, json.dumps(result_data, cls=CustomJSONEncoder), timeout)
            else:
                result_data = json.loads(result_data)

            return result_data

        return _wrapped_method

    return decorator
