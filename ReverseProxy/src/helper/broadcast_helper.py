from threading import Lock
from src.model.broadcast_states import BroadcastStates
from src.helper import session_helper

session_helper = session_helper.factory.get_session_helper()

class BroadcastHelper:

    def __init__(self):
        self.broadcast_session_info_map = {}
        self.broadcast_session_state = BroadcastStates.STOP
        self.broadcast = BroadcastStates.IDLE
        self.message = None
        self.broadcast_message_queues = {}


    def add_message_for_all(self, message):
        for key, value in self.broadcast_message_queues.items():
            value.put(message)

    def cleanup_broadcast_session(self):
        self.broadcast_session_state = BroadcastStates.STOP
        self.add_message_for_all(self.broadcast_session_state.value)

    def remove_user_from_session_info(self, user_id):
        del self.broadcast_session_info_map[user_id]

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
