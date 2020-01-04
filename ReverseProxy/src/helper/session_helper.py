from queue import Queue
from threading import Lock


class SessionHelper:

    def __init__(self):
        self.session_info_map = {}
        self.port_queue = Queue()
        self.setup_ports()

    def setup_ports(self):
        for i in range(0, 5):
            self.port_queue.put(8080 + i)

    def add_to_port_queue(self, port):
        self.port_queue.put(port)

    def get_free_port(self):
        # TODO: Change this function to return a port from a pool of available ports
        return self.port_queue.get()

    def get_session_for_user(self, user_id):
        return self.session_info_map[user_id]


class Factory:
    session_helper = None
    lock = Lock()

    def get_session_helper(self):
        with self.lock:
            if self.session_helper is not None:
                return self.session_helper
            else:
                self.session_helper = SessionHelper()
                return self.session_helper

    def reset_session_helper(self):
        with self.lock:
            self.session_helper = SessionHelper()


factory = Factory()
