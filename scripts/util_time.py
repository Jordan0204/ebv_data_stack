import datetime as dt
from typing import Tuple

def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

def floor_minute(t: dt.datetime) -> dt.datetime:
    return t.replace(second=0, microsecond=0)

def next_minute_boundary(t: dt.datetime=None) -> dt.datetime:
    t = t or now_utc()
    fm = floor_minute(t)
    return fm + dt.timedelta(minutes=1)

def hour_bounds_ending_at(hour_end: dt.datetime) -> Tuple[dt.datetime, dt.datetime]:
    start = hour_end - dt.timedelta(hours=1)
    return start, hour_end
