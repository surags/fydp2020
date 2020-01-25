import json

import requests
from bottle import response
from peewee import JOIN
from threading import Lock

from src.model.school import School
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.helper import response_format_helper
from src.model.users import Users
from src.helper import session_helper

session_helper = session_helper.factory.get_session_helper()


class UserHelper:
    def __init__(self):
        pass

    def user_info(self, username):
        try:
            join_condition = Users.school_id == School.school_id
            query = Users.select(Users, School.school_name).join(School, JOIN.INNER, on=join_condition).where(
                Users.user_name == username).dicts()
            response.body = json.dumps({'user': list(query)}, default=response_format_helper.to_serializable)
            response.status = 200
        except Exception as e:
            print(e)
            response.body = "Error: User does not exist"
            response.status = 400
        return response

    def student_list(self, school_id):
        query = Users.select(Users.user_id, Users.user_name, Users.first_name, Users.last_name).where(
            Users.user_type == "Student" and Users.school_id == school_id).dicts()
        response.body = json.dumps({'students': list(query)})
        response.status = 200
        return response

    def application_list(self):
        query = Application.select().dicts()
        response.body = json.dumps({'applications': list(query)})
        response.status = 200
        return response

    def session_list(self):
        return session_helper.get_all_sessions_that_exist()

    def permitted_apps(self, user_id):
        join_condition = ApplicationPermission.application_id == Application.application_id
        query = ApplicationPermission.select(Application.application_id, Application.application_name).join(Application,
                                                                                                            JOIN.INNER,
                                                                                                            on=join_condition).where(
            ApplicationPermission.user_id == user_id).dicts()
        response.body = json.dumps({'applications': list(query)})
        response.status = 200
        return response

    def give_access(self, user_id, application_id):
        # If this query doesn't return empty, than this permission is already in the DB
        query = ApplicationPermission.select().where(ApplicationPermission.user_id == user_id,
                                                     ApplicationPermission.application_id == application_id)
        if query.exists():
            response.body = json.dumps({'error_database': 'This permission already exists'})
            response.status = 400
        else:
            try:
                perm = ApplicationPermission()
                perm.user_id = user_id
                perm.application_id = application_id
                perm.save()
                response.body = '{"applications": "Successfully granted permission",'
                response.status = 200
            except Exception as e:
                print(str(e))
                response.body = '{"error_database": "Invalid user_id or application_id",'
                response.status = 400
        try:
            os_container_ip = session_helper.get_session_for_user(user_id).destination_ip
            self.add_application_permission_in_container(os_container_ip, application_id)
            response.body += '"containers": "Successfully added permission in container"}'
        except Exception as e:
            print(str(e))
            response.body += '"error_container": "Could not add permission to container"}'
        return response

    def revoke_access(self, user_id, application_id):
        try:
            perm = ApplicationPermission.get(
                ApplicationPermission.user_id == user_id and ApplicationPermission.application_id == application_id)
            perm.delete_instance(recursive=True)
            response.body = response.body = '{"applications": "Successfully revoked permission",'
            response.status = 200
        except Exception as e:
            print(e)
            response.body = '{"error_database": "Invalid user_id or application_id",'
            response.status = 400

        try:
            os_container_ip = session_helper.get_session_for_user(user_id).destination_ip
            self.revoke_application_permission_in_container(os_container_ip, application_id)
            response.body += '"containers": "Successfully deleted permission in container"}'
        except Exception as e:
            print(str(e))
            response.body += '"error_container": "Could not delete permission from container"}'
        return response

    def add_application_permission_in_container(self, os_container_ip, application_id):
        url = 'http://{0}:9090/application/permission/add/{1}'.format(os_container_ip, application_id)
        requests.post(url)

    def revoke_application_permission_in_container(self, os_container_ip, application_id):
        url = 'http://{0}:9090/application/permission/remove/{1}'.format(os_container_ip, application_id)
        requests.post(url)


class Factory:
    user_helper = None
    lock = Lock()

    def get_user_helper(self):
        with self.lock:
            if self.user_helper is not None:
                return self.user_helper
            else:
                self.user_helper = UserHelper()
                return self.user_helper

    def reset_helper(self):
        with self.lock:
            self.user_helper = UserHelper()
