from datetime import datetime

import pytz
from django.utils import timezone as dj_timezone


def get_current_datetime(tzname: str | None = None) -> datetime:
    now = dj_timezone.now()
    if tzname:
        now = now.astimezone(pytz.timezone(tzname))
    return now
