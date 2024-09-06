from __future__ import annotations

from abc import ABC

from rest_framework import serializers

from lexicon.utils import returndict_to_dict


class BaseEventForm(serializers.Serializer):
    pass


class BaseEvent(ABC):
    # A unique identifier for the event
    identifier = None

    # A readable label name of event
    label = None

    # A readable description of event
    description = None

    # A form for event data schema and validation
    form_cls = None

    # A django signal to which this event should be triggered/generated when
    # signal emit
    signal = None

    def __init__(self, data: dict | None = None):
        self._data = data or {}

    @property
    def data(self):
        return self._data

    def get_form_cls(self):
        return self.form_cls

    def get_form_instance(self):
        Form = self.get_form_cls()
        return Form(data=self._data)

    def render_label(self):
        return self.label.format(**self._data)

    def validate_form(self):
        if not self.get_form_cls():
            return True

        form = self.get_form_instance()
        return form.is_valid()

    def get_form_data(self):
        form = self.get_form_instance()
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)
        return returndict_to_dict(form.data)

    def get_data(self, key, default=None):
        return self._data.get(key, default)

    def get_context(self):
        return {}
