from rest_framework import generics, views
from rest_framework.response import Response

from lexicon.api.utils import prep_response_data
from lexicon.middleware.current_user import set_current_user


class ResponseMixin:
    """
    A mixin class providing methods to generate standard responses for API views.
    """

    def success_response(self, data=None, item=None, items=None, **kwargs) -> Response:
        """
        Creates a successful response with the provided data.

        Args:
            data (dict, optional): Additional data to include in the response.
            item (dict, optional): A single item to include in the response.
            items (list, optional): A list of items to include in the response.
            **kwargs: Additional keyword arguments to be passed to the Response object.

        Returns:
            Response: A Response object containing the formatted success response data.
        """
        resp_data = prep_response_data(data, item, items, success=True)
        return Response(data=resp_data, **kwargs)

    def error_response(self, data=None, item=None, items=None, **kwargs) -> Response:
        """
        Creates an error response with the provided data.

        Args:
            data (dict, optional): Additional data to include in the response.
            item (dict, optional): A single item to include in the response.
            items (list, optional): A list of items to include in the response.
            **kwargs: Additional keyword arguments to be passed to the Response object.

        Returns:
            Response: A Response object containing the formatted error response data.
        """
        resp_data = prep_response_data(data, item, items, success=False)
        return Response(data=resp_data, **kwargs)


class APIView(ResponseMixin, views.APIView):
    """
    An API view that incorporates authentication and response mixin functionality.
    """

    def perform_authentication(self, request):
        """
        Perform authentication by accessing the request user and setting the current user.

        This method is called lazily when `request.user` or `request.auth` is accessed.

        Args:
            request (Request): The HTTP request object containing user information.

        Returns:
            None
        """
        user = request.user
        set_current_user(user)


class GenericAPIView(ResponseMixin, generics.GenericAPIView):
    """
    A generic API view that incorporates authentication and response mixin functionality.
    """

    def perform_authentication(self, request):
        """
        Perform authentication by accessing the request user and setting the current user.

        This method is called lazily when `request.user` or `request.auth` is accessed.

        Args:
            request (Request): The HTTP request object containing user information.

        Returns:
            None
        """
        user = request.user
        set_current_user(user)
