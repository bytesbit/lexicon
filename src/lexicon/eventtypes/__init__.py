from typing import TypeVar

from .base import BaseEvent
from .manager import EventTypeManager

Event = TypeVar("Event", bound=BaseEvent)
default_manager = EventTypeManager()

get = default_manager.get
get_choices = default_manager.get_choices
exists = default_manager.exists
register = default_manager.register
add = default_manager.add
