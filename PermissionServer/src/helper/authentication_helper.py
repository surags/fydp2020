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
        new_user.school_id = username
        new_user.first_name = "John"
        new_user.last_name = "Smith"
        new_user.user_type = 'teacher'
        new_user.email = username + "@abc.com"
        new_user.save()
        return "Successfully Created New User", 200

    def validate_user(self, user_type_id, username, password):
        try:
            user = Users.select().where(Users.user_name == username)
            if not user:
                return False
            if bcrypt.checkpw(password.encode('utf-8'), user[0].hashed_password.encode('utf8')) and user[0].user_type_id == user_type_id:
                return True
            else:
                return False
        except peewee.DoesNotExist as e:
            return False


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
