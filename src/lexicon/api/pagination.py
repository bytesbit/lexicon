from collections import OrderedDict

from django.conf import settings
from rest_framework import pagination, status


class DefaultPageNumberPagination(pagination.PageNumberPagination):
    """
    Custom pagination class that provides pagination with page number.
    """

    page_size = settings.DEFAULT_PAGINATION_PAGE_SIZE
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = settings.DEFAULT_PAGINATION_MAX_PAGE_SIZE


class PaginatedListAPIViewMixin:
    """
    Mixin to add pagination support to a view that returns a paginated list.
    """

    LIST_RESULTS_KEY = "items"

    def list(self, request, *args, **kwargs):
        """
        List endpoint with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def get_paginated_response(self, data):
        """
        Create a paginated response with additional pagination metadata.
        """
        paginator = self.paginator
        paginated_data = OrderedDict(
            {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                self.LIST_RESULTS_KEY: data,
            }
        )
        return self.success_response(paginated_data, status=status.HTTP_200_OK)
