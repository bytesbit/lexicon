from django.db import transaction


class TransactionAwareTaskMixin(object):
    """
    A celery task base class which extended and add methods for running task
    in transaction aware environment, so that the task will run after
    transaction committed successfully and otherwise will not run. Actually,
    if you call transaction aware methods, then this class delays task
    submission until the transaction is committed successfully,
    if transaction in progress otherwise submit task instantly.

    https://browniebroke.com/blog/making-celery-work-nicely-with-django-transactions/
    """

    def delay_on_commit(self, *args, **kwargs):
        transaction.on_commit(lambda: self.delay(*args, **kwargs))
        return

    def apply_async_on_commit(self, *args, **kwargs):
        transaction.on_commit(lambda: self.apply_async(*args, **kwargs))
        return
