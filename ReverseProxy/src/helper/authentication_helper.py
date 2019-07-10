import json

import bcrypt
import peewee
from threading import Lock

from bottle import response

from src.model.student import Student
from src.model.teacher import Teacher
from src.model.users import Users


class AuthenticationHelper:
    def __init__(self):
        pass

    def create_new_user(self, username, password, query):
        try:
            new_user = Users()
            new_user.user_name = username
            new_user.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_user.school_id = query.school_id
            new_user.first_name = query.first_name
            new_user.last_name = query.last_name
            new_user.user_type = query.user_type
            new_user.email = query.email
            new_user.save()
            if query.user_type.lower() == "teacher":
                new_teacher = Teacher()
                new_teacher.user_id = new_user.user_id
                new_teacher.has_system_access = True
                new_teacher.save()

                response.body = json.dumps({'success': 'Successfully created teacher ' + new_user.user_name + ' with id ' + str(new_user.user_id), 'id': new_user.user_id})
                response.status = 200
            elif query.user_type.lower() == "student":
                new_student = Student()
                new_student.user_id = new_user.user_id
                new_student.has_system_access = False
                new_student.save()

                response.body = json.dumps({'success': 'Successfully created student ' + new_user.user_name + ' with id ' + str(new_user.user_id), 'id': new_user.user_id})
                response.status = 200
            else:
                response.body = json.dumps({'error': 'Unknown user type'})
                response.status = 500

        except Exception as e:
            response.body = json.dumps({'error': str(e)})
            response.status = 500
        return response

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

    def delete_user(self, user_id):
        try:
            user = Users.get(Users.user_id == user_id)
            user.delete_instance(recursive=True)
            response.body = json.dumps({'user': 'Successfully deleted user ' + user_id})
            response.status = 200
        except peewee.DoesNotExist as e:
            response.body = json.dumps({'error': 'User does not exist'})
            response.status = 400
        except Exception as e:
            response.body = json.dumps({'error': str(e)})
            response.status = 500
        return response


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
