from functools import singledispatch
from datetime import datetime
from threading import Lock


class ResponseFormatHelper:

    @singledispatch
    def to_serializable(self, val):
        """Used by default."""
        return str(val)

    @to_serializable.register(datetime)
    def ts_datetime(self, val):
        """Used if *val* is an instance of datetime."""
        return val.isoformat() + "Z"


class Factory:
    response_format_helper = None
    lock = Lock()

    def get_response_format_helper(self):
        with self.lock:
            if self.response_format_helper is not None:
                return self.response_format_helper
            else:
                self.response_format_helper = ResponseFormatHelper()
                return self.response_format_helper

    def reset_response_format_helper(self):
        with self.lock:
            self.response_format_helper = ResponseFormatHelper()
