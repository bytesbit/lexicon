import logging
from typing import TYPE_CHECKING, Any, Type

from django.dispatch.dispatcher import Signal

from lexicon.utils import to_snakecase

if TYPE_CHECKING:
    from lexicon.eventtypes import Event

logger = logging.getLogger(__name__)


class EventProcessor:
    def __init__(self, event_id: str, data: dict):
        self._event_id = event_id
        self._data = data

    def get_event_class(self) -> Type["Event"]:
        from lexicon import eventtypes

        EventClass = eventtypes.get(self._event_id)
        return EventClass

    def get_event(self) -> "Event":
        EventClass = self.get_event_class()
        event = EventClass(data=self._data)
        return event

    def save(self, now=False):
        """Process the event

        Args:
            now (bool, optional): Process immediately or later. Defaults to False.
        """
        from lexicon.clients.tasks import process_event

        event = self.get_event()
        if not event.validate_form():
            logger.warning(f"Event data is not valid, skip {event} processing")
            return

        if now:
            process_event(event=event)

        process_event.apply_async_on_commit(kwargs={"event": event}, serializer="pickle")

    @staticmethod
    def as_signal_receiver(event_id: str):
        def signal_receiver(signal: Signal, sender: Any, **kwargs):
            EventProcessor(event_id, data=kwargs).save()
            logger.info(
                "Event processor processed signal receiver successfully",
                extra={"event_id": event_id},
            )
            return

        return signal_receiver

    @staticmethod
    def register_signal_receiver(signal: Signal, event_cls: Type["Event"]):
        event_id = event_cls.identifier
        dispatch_uid = "event_processor_%s" % to_snakecase(event_id)
        signal.connect(
            EventProcessor.as_signal_receiver(event_id),
            dispatch_uid=dispatch_uid,
            weak=False,
        )
        logger.debug('Receiver "%s" for signal is registered', dispatch_uid)
