from threading import Lock


class UserInfoManager:
    def __init__(self):
        self.user_id = ""

class Factory:
    def __init__(self):
        self.user_info_manager = None
        self.lock = Lock()

    def get_user_info_manager(self):
        with self.lock:
            if self.user_info_manager is not None:
                return self.user_info_manager
            else:
                self.user_info_manager = UserInfoManager()
                return self.user_info_manager

    def reset_user_info_manager(self):
        with self.lock:
            self.user_info_manager = UserInfoManager()


factory = Factory()
