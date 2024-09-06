import abc

from django.db.models import QuerySet


class BaseQuerySet(QuerySet, abc.ABC):  # type: ignore
    def defer(self, *args, **kwargs) -> "BaseQuerySet":
        raise NotImplementedError("Use ``values_list`` instead [performance].")

    def only(self, *args, **kwargs) -> "BaseQuerySet":
        # In rare cases Django can use this if a field is unexpectedly
        # deferred. This mostly can happen if a field is added to a model,
        # and then an old pickle is passed to a process running the new
        # code. So if you see this error after a deploy of a model with a
        # new field, it'll likely fix itself post-deploy.
        raise NotImplementedError("Use ``values_list`` instead [performance].")
