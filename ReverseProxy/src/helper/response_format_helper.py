from functools import singledispatch
from datetime import datetime

@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register(datetime)
def ts_datetime(val):
    """Used if *val* is an instance of datetime."""
    return val.isoformat() + "Z"
