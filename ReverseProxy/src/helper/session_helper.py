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
    
    def get_all_destination_ip(self):
        userIds = list(self.session_info_map.keys())
        destination_ip = list()

        for key in userIds:
            destination_ip.append(self.session_info_map[key].destination_ip)
        
        return destination_ip

    def get_all_sessions_that_exist(self):
        userIds = list(self.session_info_map.keys())
        response = '{"users_with_sessions": ['
        for idx, key in enumerate(userIds):
            if idx == len(userIds) - 1:
                response += '{"userID":' + key + ',' + '"first_name": "' + self.session_info_map[key].first_name + '",' \
                            + '"last_name": "' + self.session_info_map[key].last_name + '"}'
            else:
                response += '{"userID":' + key + ',' + '"first_name": "' + self.session_info_map[key].first_name + '",' \
                            + '"last_name": "' + self.session_info_map[key].last_name + '"},'
        response += ']}'
        return response

    def update_all_health_checks(self, is_enabled):
        for key, value in self.session_info_map.items():
            value.is_health_check_enabled = is_enabled

    def update_health_check(self, user_id, is_enabled):
        if user_id in self.session_info_map:
            self.session_info_map[user_id].is_health_check_enabled = is_enabled

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
