from django.dispatch.dispatcher import Signal


class EventTypeManager:
    def __init__(self):
        self.__values = []
        self.__lookup = {}

    def __iter__(self):
        return iter(self.__values)

    def get_all(self):
        return list(self.__values)

    def __contains__(self, key):
        return key in self.__lookup

    def get(self, key, **kwargs):
        return self.__lookup[key]

    def exists(self, key):
        return key in self.__lookup

    def register(self):
        manager = self

        def wrapped_register(cls):
            manager.add(cls)
            return cls

        return wrapped_register

    def add(self, cls):
        self.__values.append(cls)
        self.__lookup[cls.identifier] = cls

        # register the signal receiver, if signal is set
        signal = getattr(cls, "signal")
        if signal and isinstance(signal, Signal):
            from lexicon.eventtypes.processor import EventProcessor

            EventProcessor.register_signal_receiver(signal, cls)

    def get_choices(self):
        return tuple((event_cls.identifier, event_cls.label) for event_cls in self.__values)
