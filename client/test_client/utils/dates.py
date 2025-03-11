# ====================================================================
# dates.py
# ====================================================================

import datetime


# --------------------------------------------------------------------
# convert_to_unix_time
#
# --------------------------------------------------------------------
def convert_to_unix_time(dt: datetime.datetime) -> float:
    return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())


# --------------------------------------------------------------------
# parse_unix_time
#
# --------------------------------------------------------------------
def parse_unix_time(unix_time: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(unix_time, datetime.timezone.utc)
