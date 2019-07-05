import bcrypt
import peewee
from threading import Lock
from src.model.users import Users


class AuthenticationHelper:
    def __init__(self):
        pass

    def create_new_user(self, username, password):
        new_user = Users()
        new_user.user_name = username
        new_user.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user.school_id = "temp_id"
        new_user.first_name = "John"
        new_user.last_name = "Smith"
        new_user.email = "johnsmith@abc.com"
        new_user.save()
        return "Successfully Created New User", 200

    def validate_user(self, user_id, password):
        try:
            user = Users.get_by_id(user_id)
            if bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf8')):
                print("Success")
                return "Successfully Authenticated", 200
            else:
                print("Failed")
                return "Failed Authentication", 401
        except peewee.DoesNotExist as e:
            return "Failed Authentication", 401


class Factory:
    authentication_helper = None
    lock = Lock()

    def get_authentication_helper(self):
        with self.lock:
            if self.authentication_helper is not None:
                return self.authentication_helper
            else:
                self.authentication_helper = AuthenticationHelper()
                return self.authentication_helper

    def reset_router(self):
        with self.lock:
            self.authentication_helper = AuthenticationHelper()
