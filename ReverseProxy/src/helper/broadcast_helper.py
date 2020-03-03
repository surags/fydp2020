from threading import Lock

class BroadcastHelper:

    def __init__(self):
        self.broadcast = None
        self.message = None


class Factory:
    broadcast_helper = None
    lock = Lock()

    def get_broadcast_helper(self):
        with self.lock:
            if self.broadcast_helper is not None:
                return self.broadcast_helper
            else:
                self.broadcast_helper = BroadcastHelper()
                return self.broadcast_helper

    def reset_session_helper(self):
        with self.lock:
            self.broadcast_helper = BroadcastHelper()

factory = Factory()
