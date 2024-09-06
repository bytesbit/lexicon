from typing import TypeVar

from django.db.models import Model

M = TypeVar("M", bound=Model)

# Exporting these classes at the bottom to avoid circular dependencies.
from .base import BaseManager
from .base_query_set import BaseQuerySet
